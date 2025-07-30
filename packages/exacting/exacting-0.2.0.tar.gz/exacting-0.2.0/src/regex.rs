use fancy_regex::Regex;

use pyo3::{ exceptions, prelude::* };

#[pyclass(name = "Regex")]
pub(crate) struct PyRegex {
    regex: Regex,
}

#[pymethods]
impl PyRegex {
    #[new]
    pub(crate) fn py_new(m: &str) -> PyResult<Self> {
        let Ok(re) = Regex::new(m) else {
            return Err(exceptions::PyRuntimeError::new_err("Failed to parse & compile regex"));
        };

        Ok(Self { regex: re })
    }

    pub(crate) fn validate(&self, input: &str) -> PyResult<bool> {
        let Ok(res) = self.regex.is_match(input) else {
            return Err(exceptions::PyRuntimeError::new_err("Failed to match regex"));
        };
        Ok(res)
    }
}
