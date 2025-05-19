pub mod llm_types;
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct Model {
    pub key: String,
    pub enabled: bool,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct ModelProvider {
    pub name: String,
    pub base_url: String,
    pub token_env_var: Option<String>,
    pub models: Vec<Model>,
    pub enabled: bool,
}


/// Parameters for a test that will need a rerun if they have changed.
#[derive(Serialize, Deserialize, Debug, Clone, PartialEq)]
pub struct TestParameters {

    pub docker_image: String,
    pub initial_prompt: Vec<llm_types::Message>,
    pub allowed_tools: Vec<Tools>,
}


/// The parametrs of a test as stored on disk used to configure a test.
/// Some parameters will not cause a rerun (eg name). All parametesr that
/// will cause a rerun should be contained in the test_parameters: TestParameters
/// field rather than directly in this struct.
#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct TestConfig {
    pub name: String,
    pub blurb: String,
    pub tags: Vec<String>,
    #[serde(flatten)]
    pub test_parameters: TestParameters,
}


#[derive(Serialize, Deserialize, Debug, Clone)]
#[serde(rename_all = "snake_case")]
pub enum FinishReason {
    TaskCompleteTool,
    EmptyContent,
    IterationLimit(usize),
}

#[derive(Serialize, Deserialize, Debug)]
pub struct ResultStats {
    pub run_date: Option<DateTime<Utc>>,
    pub time_seconds: f64,
    pub log: Vec<llm_types::Message>,
    pub finish_reason: Option<FinishReason>,
}

#[derive(Serialize, Deserialize, Debug, PartialEq, Clone)]
#[serde(rename_all = "snake_case")]
pub enum Tools {
    Bash,
    CreateFile,
}

/// All the parameters for a test. Some of these (eg name) won't cause a
/// rerun of the test if they change. All of the ones contained in
/// test_parameters: TestParameters will cause a rerun if they change.
#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct TestToRun {
    pub name: String,
    pub test_parameters: TestConfig,
    pub provider: ModelProvider,
    pub model: Model,
    pub input_folder: String,
    pub output_folder: String,
}
