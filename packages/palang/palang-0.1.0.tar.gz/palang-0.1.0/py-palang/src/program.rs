use std::{env, fs, path::PathBuf};

use palang_compiler::compile_file;
use palang_core::profile::{load_profile, Profile};
use palang_virtual_machine::{assembly::{assembly::Assembly, loader::load_assembly, return_type_coercion::ReturnTypeCoercion}, boot_machine, choose_llm, llm::llm::LargeLanguageModel, virtualization::virtual_machine::VirtualMachine};
use pyo3::prelude::*;
use tokio::runtime::Runtime;

#[pyclass]
pub struct Program {
    task: String,
}

#[pymethods]
impl Program {
    #[new]
    pub fn new(task: String) -> Self {
        Program { task }
    }

    pub fn with_model(&self, profile_name: String) -> PyResult<RunnableProgram> {
        let profile_path: PathBuf = env::current_dir()?
            .join("palang")
            .join("profiles")
            .join(format!("{}.yaml", profile_name));

        let profile: Profile = load_profile(&profile_path).unwrap();

        let llm: LargeLanguageModel = choose_llm(&profile.llm).unwrap();

        let program_path: PathBuf = env::current_dir()?
            .join("hello.palang");

        let source_code: String = fs::read_to_string(program_path)?;
        let assembly_code: String = compile_file(&source_code).unwrap();
        let assembly: Assembly = load_assembly(&assembly_code).unwrap();

        let mut vm: VirtualMachine = boot_machine(&llm);
        vm.load_assembly(&assembly);

        Ok(RunnableProgram::new(profile, vm, self.task.clone()))
    }
}

#[pyclass]
pub struct RunnableProgram {
    profile: Profile,
    vm: VirtualMachine,
    task: String,
}

impl RunnableProgram {
    pub fn new(profile: Profile, vm: VirtualMachine, task: String) -> Self {
        RunnableProgram { profile, vm, task }
    }
}

#[pymethods]
impl RunnableProgram {
    pub fn __call__(&mut self) -> PyResult<String> {
        let runtime: Runtime = tokio::runtime::Runtime::new().unwrap();

        let result: Result<String, String> = runtime.block_on(async {
            self.vm.execute(
                &self.task.replace("::", "/"),
                &Vec::new(),
                &ReturnTypeCoercion::NotCoerced,
                &self.profile,
            ).await.await
        });

        Ok(result.unwrap())
    }
}
