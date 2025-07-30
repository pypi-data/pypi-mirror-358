use pyo3::prelude::*;

use crate::program::{Program, RunnableProgram};

#[pyclass]
pub struct ProgramImporter {
    path: Vec<String>,
}

#[pymethods]
impl ProgramImporter {
    #[new]
    pub fn new() -> Self {
        ProgramImporter { path: Vec::new() }
    }

    fn __getattr__(&self, name: &str) -> Self {
        let mut new_path = self.path.clone();
        new_path.push(name.to_string());
        ProgramImporter { path: new_path }
    }

    fn with_model(&self, profile_name: String) -> PyResult<RunnableProgram> {
        let task = self.path.join("::");
        let program = Program::new(task);
        program.with_model(profile_name)
    }
}
