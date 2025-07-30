use pyo3::prelude::*;

mod json;
mod regex;
mod dump;

#[pymodule]
fn exacting(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(json::json_to_py, m)?)?;
    m.add_function(wrap_pyfunction!(json::jsonc_to_py, m)?)?;
    m.add_function(wrap_pyfunction!(dump::py_to_bytes, m)?)?;
    m.add_function(wrap_pyfunction!(dump::bytes_to_py, m)?)?;

    m.add_class::<regex::PyRegex>()?;
    Ok(())
}
