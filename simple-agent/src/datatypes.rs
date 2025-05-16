use super::llm_api::types::Message;
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug)]
#[serde(rename_all = "snake_case")]
pub enum FinishReason {
    TaskCompleteTool,
    EmptyContent,
    IterationLimit(usize),
}

#[derive(Serialize, Deserialize, Debug)]
pub struct ModelProvider {
    pub name: String,
    pub base_url: String,
    pub token: String,
    pub models: Vec<String>,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct ResultStats {
    pub run_date: Option<DateTime<Utc>>,
    pub time_seconds: f64,
    pub log: Vec<Message>,
    pub finish_reason: Option<FinishReason>,
}

#[derive(Serialize, Deserialize, Debug, PartialEq)]
#[serde(rename_all = "snake_case")]
pub enum Tools {
    Bash,
    CreateFile,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct TestParameters {
    pub docker_image: String,
    pub initial_prompt: Vec<Message>,
    pub allowed_tools: Vec<Tools>,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct TestToRun {
    pub test_parameters: TestParameters,
    pub provider: ModelProvider,
    pub model: String,
    pub input_folder: String,
    pub output_folder: String,
}
