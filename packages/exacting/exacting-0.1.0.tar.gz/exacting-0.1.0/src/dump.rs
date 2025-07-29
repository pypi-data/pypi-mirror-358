use std::collections::HashMap;

use rkyv::{ rancor, Archive, Serialize, Deserialize };
use pyo3::{ exceptions, prelude::*, types::{ PyBytes, PyDict, PyList, PyNone } };

#[derive(Archive, Serialize, Deserialize, PartialEq)]
pub(crate) enum Model {
    Str(String),
    Int(i64),
    Float(f64),
    Bool(bool),
    Bytes(Vec<u8>),
    None,

    List(Vec<Vec<u8>>),
    Dict(HashMap<Vec<u8>, Vec<u8>>),
}

impl Model {
    fn from_bytes(py: Python, bytes: &[u8]) -> PyResult<AnyPy> {
        let Ok(model) = rkyv::from_bytes::<Model, rancor::Error>(bytes) else {
            return Err(
                exceptions::PyRuntimeError::new_err("Failed to convert to model from bytes")
            );
        };

        match model {
            Self::Bool(b) => Ok(AnyPy::Bool(b)),
            Self::Bytes(b) => Ok(AnyPy::Bytes(PyBytes::new(py, &b).unbind())),
            Self::Dict(mut d) => {
                let dict = PyDict::new(py);

                for (k, v) in d.drain() {
                    dict.set_item(Model::from_bytes(py, &k)?, Model::from_bytes(py, &v)?)?;
                }

                Ok(AnyPy::Dict(dict.unbind()))
            }
            Self::Float(float) => Ok(AnyPy::Float(float)),
            Self::Int(int) => Ok(AnyPy::Int(int)),
            Self::List(mut vec) => {
                let list = PyList::empty(py);
                for item in vec.drain(..) {
                    list.append(Model::from_bytes(py, &item)?)?;
                }

                Ok(AnyPy::List(list.unbind()))
            }
            Self::None => Ok(AnyPy::None(PyNone::get(py).extract::<Py<PyNone>>()?)),
            Self::Str(string) => Ok(AnyPy::Str(string)),
        }
    }
}

#[derive(FromPyObject, IntoPyObject)]
pub(crate) enum AnyPy {
    List(Py<PyList>),
    Dict(Py<PyDict>),
    Str(String),
    Bool(bool),
    #[allow(dead_code)] None(Py<PyNone>),
    Int(i64),
    Float(f64),
    Bytes(Py<PyBytes>),
}

impl AnyPy {
    fn into_model(self, py: Python) -> PyResult<Model> {
        match self {
            Self::Bool(b) => Ok(Model::Bool(b)),
            Self::Dict(d) => {
                let mut hm = HashMap::new();
                for (key, value) in d.bind(py).iter() {
                    let k = key.extract::<AnyPy>()?;
                    let v = value.extract::<AnyPy>()?;
                    hm.insert(k.into_bytes(py)?, v.into_bytes(py)?);
                }

                Ok(Model::Dict(hm))
            }
            Self::Bytes(bytes) => {
                let b = bytes.bind(py).extract::<Vec<u8>>()?;
                Ok(Model::Bytes(b))
            }
            Self::Float(float) => { Ok(Model::Float(float)) }
            Self::Int(int) => { Ok(Model::Int(int)) }
            Self::List(list) => {
                let mut v = Vec::new();
                for item in list.bind(py) {
                    v.push(item.extract::<AnyPy>()?.into_bytes(py)?);
                }

                Ok(Model::List(v))
            }
            Self::None(_) => { Ok(Model::None) }
            Self::Str(string) => { Ok(Model::Str(string)) }
        }
    }

    fn into_bytes(self, py: Python) -> PyResult<Vec<u8>> {
        let Ok(d) = rkyv::to_bytes::<rancor::Error>(&self.into_model(py)?) else {
            return Err(exceptions::PyRuntimeError::new_err("Failed to convert to bytes"));
        };

        Ok(d.into())
    }
}

#[pyfunction]
pub(crate) fn py_to_bytes(py: Python, data: AnyPy) -> PyResult<Py<PyBytes>> {
    Ok(PyBytes::new(py, &data.into_bytes(py)?).unbind())
}

#[pyfunction]
pub(crate) fn bytes_to_py(py: Python, bytes: &[u8]) -> PyResult<AnyPy> {
    Model::from_bytes(py, bytes)
}
