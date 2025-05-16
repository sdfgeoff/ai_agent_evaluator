use std::pin::Pin;

use crate::{
    llm_api::types::{ToolDefinition, ToolFunction, ToolFunctionType},
    tool_manager::ToolAndCallable,
};
use serde::{Deserialize, Serialize};
use serde_json::Value;

#[derive(Serialize, Deserialize, Debug)]
#[serde(rename_all = "snake_case")]
enum TextContentType {
    Text,
    Image,
}

#[derive(Serialize, Deserialize, Debug)]
struct TextContent {
    #[serde(rename = "type")]
    type_: TextContentType,
    text: String,
}

#[derive(Serialize, Deserialize, Debug)]
struct BashArguments {
    command: String,
}

pub struct BashTool {}

#[derive(Serialize, Deserialize, Debug)]
struct BashResult {
    output: Option<String>,
    error: Option<String>,
    exit_code: Option<i32>,
}
impl ToolAndCallable for BashTool {
    fn definition(&self) -> ToolDefinition {
        ToolDefinition {
            type_: ToolFunctionType::Function,
            function: ToolFunction {
                name: "bash".to_string(),
                description: Some("Run a bash command.".to_string()),
                parameters: serde_json::from_str(
                    r#"{
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The command to run."
                        }
                    },
                    "required": ["command"]
                }"#,
                )
                .unwrap(),
            },
        }
    }

    fn call(
        &self,
        arguments: String,
    ) -> Pin<Box<dyn Future<Output = Result<Value, String>> + Send>> {
        Box::pin(async move {
            let args: BashArguments =
                serde_json::from_str(&arguments).map_err(|e| e.to_string())?;
            let output = tokio::process::Command::new("bash")
                .arg("-c")
                .arg(&args.command)
                .output()
                .await
                .map_err(|e| e.to_string())?;

            let result = BashResult {
                output: if output.stdout.is_empty() {
                    None
                } else {
                    Some(String::from_utf8_lossy(&output.stdout).to_string())
                },
                error: if output.stderr.is_empty() {
                    None
                } else {
                    Some(String::from_utf8_lossy(&output.stderr).to_string())
                },
                exit_code: Some(output.status.code().unwrap_or(-1)),
            };

            Ok(serde_json::to_value(vec![TextContent {
                type_: TextContentType::Text,
                text: serde_json::to_string(&result).unwrap(),
            }])
            .unwrap())
        })
    }
}

pub struct CreateFileTool {}
#[derive(Serialize, Deserialize, Debug)]
struct CreateFileArguments {
    file_name: String,
    content: String,
}

impl ToolAndCallable for CreateFileTool {
    fn definition(&self) -> ToolDefinition {
        ToolDefinition {
            type_: ToolFunctionType::Function,
            function: ToolFunction {
                name: "create_file".to_string(),
                description: Some("Create a file.".to_string()),
                parameters: serde_json::from_str(
                    r#"{
                    "type": "object",
                    "properties": {
                        "file_name": {
                            "type": "string",
                            "description": "The name of the file to create."
                        },
                        "content": {
                            "type": "string",
                            "description": "The content of the file."
                        }
                    },
                    "required": ["file_name", "content"]
                }"#,
                )
                .unwrap(),
            },
        }
    }
    fn call(
        &self,
        arguments: String,
    ) -> Pin<Box<dyn Future<Output = Result<Value, String>> + Send>> {
        Box::pin(async move {
            let args: CreateFileArguments =
                serde_json::from_str(&arguments).map_err(|e| e.to_string())?;
            let file_path = format!("./{}", args.file_name);
            std::fs::write(&file_path, args.content).map_err(|e| e.to_string())?;
            Ok(serde_json::to_value(vec![TextContent {
                type_: TextContentType::Text,
                text: format!("File created at {}", file_path),
            }])
            .unwrap())
        })
    }
}
