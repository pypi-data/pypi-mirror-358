// IMPORT
mod cryptography; use cryptography::quantum;
use pyo3::prelude::*;

// MAIN
#[pymodule]
fn __internal__(module: &Bound<PyModule>) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(quantum::binding::sigkeygen, module)?)?;
    module.add_function(wrap_pyfunction!(quantum::binding::sigsign, module)?)?;
    module.add_function(wrap_pyfunction!(quantum::binding::sigverify, module)?)?;
    //
    module.add_function(wrap_pyfunction!(quantum::binding::kemkeygen, module)?)?;
    module.add_function(wrap_pyfunction!(quantum::binding::kemencapsulate, module)?)?;
    module.add_function(wrap_pyfunction!(quantum::binding::kemdecapsulate, module)?)?;
    Ok(())
}
