#![warn(clippy::all, clippy::cargo, clippy::pedantic)]
#![allow(clippy::module_name_repetitions)] // Allows for better API naming

pub mod constant;
pub mod data;
pub mod disassembly;
pub mod error;
pub mod extractor;
pub mod layout;
pub mod opcode;
pub mod tc;
pub mod utility;
pub mod vm;
pub mod watchdog;
// mod common;

// Re-exports to provide the library interface.
pub use extractor::new;
pub use layout::StorageLayout;

use pyo3::prelude::*;
use pyo3::exceptions::PyRuntimeError;
use crate::extractor::{
    chain::{version::EthereumVersion, Chain},
    contract::Contract,
};
use crate as sle;
use crate::layout::StorageSlot;
use std::time::Duration;

#[pyclass]
#[derive(Clone)]
pub struct PyStorageSlot {
    #[pyo3(get, set)]
    pub index: String,
    #[pyo3(get, set)]
    pub offset: usize,
    #[pyo3(get, set)]
    pub typ: String,
}

#[pymethods]
impl PyStorageSlot {
    pub fn to_dict(&self, py: Python) -> PyResult<PyObject> {
        let dict = pyo3::types::PyDict::new(py);
        dict.set_item("index", self.index.clone())?;
        dict.set_item("offset", self.offset.clone())?;
        dict.set_item("typ", self.typ.clone())?;
        Ok(dict.into())
    }
}

impl From<StorageSlot> for PyStorageSlot {
    fn from(slot: StorageSlot) -> Self {
        PyStorageSlot {
            index: format!("{:?}", slot.index),
            offset: slot.offset,
            typ: slot.typ.to_solidity_type(),
        }
    }
}

#[pymodule]
fn storage_layout_extractor(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyStorageSlot>()?;
    m.add_function(wrap_pyfunction!(extract_storage, m)?)?;
    Ok(())
}

#[pyfunction]
fn extract_storage(bytecode_str: String) -> PyResult<Vec<PyStorageSlot>> {
    // Strip 0x prefix if present
    let bytecode_str = bytecode_str.strip_prefix("0x").unwrap_or(&bytecode_str);
    
    // Decode the hexadecimal string to bytes
    let bytes = hex::decode(bytecode_str)
        .map_err(|e| PyRuntimeError::new_err(format!("Failed to decode bytecode: {}", e)))?;

    // Construct a Contract object and perform the analysis
    let contract = Contract::new(
        bytes,
        Chain::Ethereum {
            version: EthereumVersion::Shanghai,
        },
    );

    // Create a new tokio runtime and block on the async function
    let runtime = tokio::runtime::Runtime::new()
        .map_err(|e| PyRuntimeError::new_err(format!("Failed to create runtime: {}", e)))?;
    
    let result = runtime.block_on(async move {
        tokio::time::timeout(
            Duration::from_secs(10),
            tokio::task::spawn_blocking(move || {
                sle::new(
                    contract,
                    vm::Config::default(),
                    tc::Config::default(),
                    watchdog::LazyWatchdog.in_rc(),
                )
                .analyze()
            }),
        )
        .await
    });
    
    match result {
        Ok(Ok(Ok(layout))) => {
            let py_slots: Vec<PyStorageSlot> = layout
                .slots()
                .iter()
                .map(|slot| slot.clone().into())
                .collect();
            Ok(py_slots)
        }
        Ok(Ok(Err(e))) => {
            Err(PyRuntimeError::new_err(format!("Analysis failed: {}", e)))
        }
        Ok(Err(e)) => {
            Err(PyRuntimeError::new_err(format!("Thread panicked: {}", e)))
        }
        Err(_) => {
            // Timeout occurred, return empty vector
            Ok(Vec::new())
        }
    }
}
