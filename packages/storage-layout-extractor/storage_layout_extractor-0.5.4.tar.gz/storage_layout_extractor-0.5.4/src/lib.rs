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
use pyo3::exceptions;
use pyo3_asyncio::tokio as pyo3_tokio;
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
fn storage_layout_extractor(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(extract_storage, m)?)?;
    Ok(())
}

#[pyfunction]
fn extract_storage<'py>(py: Python<'py>, bytecode_str: String) -> PyResult<&'py PyAny> {
    pyo3_tokio::future_into_py(py, async move {
        // Decode the hexadecimal string to bytes
        let bytes = match hex::decode(bytecode_str) {
            Ok(b) => b,
            Err(e) => {
                return Python::with_gil(|py| {
                    Err(PyErr::new::<exceptions::PyValueError, _>(
                        format!("Failed to decode bytecode: {}", e),
                    ))
                });
            }
        };

        // Construct a Contract object and perform the analysis
        let contract = Contract::new(
            bytes,
            Chain::Ethereum {
                version: EthereumVersion::Shanghai,
            },
        );

        match tokio::time::timeout(
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
        {
            Ok(Ok(Ok(layout))) => {
                let py_slots: Vec<PyStorageSlot> = layout
                    .slots()
                    .iter()
                    .map(|slot| slot.clone().into())
                    .collect();

                Python::with_gil(|py| Ok(py_slots.into_py(py)))
            }
            Ok(Ok(Err(e))) => Python::with_gil(|py| {
                Err(PyErr::new::<exceptions::PyRuntimeError, _>(format!(
                    "Analysis failed: {}",
                    e
                )))
            }),
            Ok(Err(e)) => Python::with_gil(|py| {
                Err(PyErr::new::<exceptions::PyRuntimeError, _>(format!(
                    "Thread panicked: {}",
                    e
                )))
            }),
            Err(_) => Python::with_gil(|py| Ok(Vec::<PyStorageSlot>::new().into_py(py))),
        }
    })
}
