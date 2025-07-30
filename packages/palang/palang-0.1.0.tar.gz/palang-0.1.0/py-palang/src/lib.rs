use pyo3::prelude::*;

use crate::{import::ProgramImporter, program::{Program, RunnableProgram}};

mod import;
mod program;

#[pymodule]
fn palang(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<ProgramImporter>()?;
    m.add_class::<Program>()?;
    m.add_class::<RunnableProgram>()?;
    
    // Create and expose the root importer
    let importer = ProgramImporter::new();
    m.add("use", importer)?;

    Ok(())
}
