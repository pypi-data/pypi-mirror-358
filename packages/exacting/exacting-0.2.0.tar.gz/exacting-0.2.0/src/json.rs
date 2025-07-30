use pyo3::{
    exceptions,
    prelude::*,
    types::{ PyBool, PyDict, PyFloat, PyInt, PyList, PyNone, PyString },
};

use ijson::{ IValue, ValueType };

#[pyfunction]
pub(crate) fn json_to_py(py: Python, json: &str) -> PyResult<Py<PyAny>> {
    let value = match serde_json::from_str::<IValue>(json) {
        Ok(d) => d,
        Err(e) => {
            return Err(
                exceptions::PyRuntimeError::new_err(format!("Failed to load JSON:\n{:#?}", e))
            );
        }
    };
    ivalue_to_py(py, value)
}

#[pyfunction]
pub(crate) fn jsonc_to_py(py: Python, json: &str) -> PyResult<Py<PyAny>> {
    let value = match serde_json5::from_str::<IValue>(json) {
        Ok(d) => d,
        Err(e) => {
            return Err(
                exceptions::PyRuntimeError::new_err(format!("Failed to load JSONC:\n{:#?}", e))
            );
        }
    };
    ivalue_to_py(py, value)
}

fn ivalue_to_py(py: Python, value: IValue) -> PyResult<Py<PyAny>> {
    match value.type_() {
        ValueType::Array => {
            let list = PyList::empty(py);
            let Ok(array) = value.into_array() else {
                return Err(exceptions::PyRuntimeError::new_err("Failed to convert into array"));
            };

            for item in array {
                let value = ivalue_to_py(py, item)?;
                list.append(value)?;
            }

            Ok(list.unbind().into())
        }
        ValueType::Bool => {
            let b = PyBool::new(py, value.to_bool().unwrap());
            Ok(unsafe { Py::from_borrowed_ptr_or_opt(py, b.as_ptr()).unwrap() })
        }
        ValueType::Null => {
            let none = PyNone::get(py);
            Ok(unsafe { Py::from_borrowed_ptr_or_opt(py, none.as_ptr()).unwrap() })
        }
        ValueType::Number => {
            let Ok(number) = value.into_number() else {
                return Err(exceptions::PyRuntimeError::new_err("Failed to convert into number"));
            };

            if number.has_decimal_point() {
                Ok(PyFloat::new(py, number.to_f64().unwrap()).unbind().into())
            } else {
                Ok(PyInt::new(py, number.to_i64().unwrap()).unbind().into())
            }
        }
        ValueType::Object => {
            let Ok(object) = value.into_object() else {
                return Err(exceptions::PyRuntimeError::new_err("Failed to convert into object"));
            };

            let dict = PyDict::new(py);
            for (key, value) in object {
                dict.set_item(key.as_str(), ivalue_to_py(py, value)?)?;
            }

            Ok(dict.unbind().into())
        }
        ValueType::String => {
            let Ok(s) = value.into_string() else {
                return Err(exceptions::PyRuntimeError::new_err("Failed to convert into string"));
            };
            Ok(PyString::new(py, s.as_str()).unbind().into())
        }
    }
}
