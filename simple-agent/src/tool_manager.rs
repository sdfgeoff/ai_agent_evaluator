use std::collections::HashMap;

use crate::llm_api::types::{Message, Role, ToolCall, ToolDefinition, ToolResponseMessage};
use serde_json::Value;

pub trait ToolAndCallable {
    fn definition(&self) -> ToolDefinition;
    fn call(&self, arguments: String) -> Result<Value, String>;
}

pub struct ToolManager {
    tools_by_name: HashMap<String, Box<dyn ToolAndCallable>>,
    tool_definitions: Vec<ToolDefinition>,
}

impl ToolManager {
    pub fn new(extra_tools: Vec<Box<dyn ToolAndCallable>>) -> Self {
        let mut tools_by_name = HashMap::new();
        let mut tool_definitions = Vec::new();
        for tool in extra_tools {
            let def = tool.definition();
            let name = def.function.name.clone();
            let already_exists = tools_by_name.insert(name, tool);
            if already_exists.is_some() {
                panic!("Tool with the same name already exists");
            }
            tool_definitions.push(def);
        }

        Self {
            tools_by_name,
            tool_definitions,
        }
    }

    pub async fn get_tools(&self) -> Vec<ToolDefinition> {
        return self.tool_definitions.clone();
    }

    pub async fn call_tool(&self, call: ToolCall) -> Message {
        let arguments = call.function.arguments;
        let tool = self.tools_by_name.get(&call.function.name);

        match tool {
            Some(tool) => {
                let res = tool.call(arguments);

                match res {
                    Ok(res) => {
                        return Message::ToolResponseMessage(ToolResponseMessage {
                            tool_call_id: call.id,
                            role: Role::Tool,
                            name: call.function.name.clone(),
                            content: res,
                        });
                    }
                    Err(err) => {
                        return Message::ToolResponseMessage(ToolResponseMessage {
                            tool_call_id: call.id,
                            role: Role::Tool,
                            name: call.function.name.clone(),
                            content: Value::String(format!("ERROR: {}", err)),
                        });
                    }
                }
            }
            None => {
                return Message::ToolResponseMessage(ToolResponseMessage {
                    tool_call_id: call.id,
                    role: Role::Tool,
                    name: call.function.name.clone(),
                    content: Value::String(format!(
                        "ERROR: Tool `{}` not found",
                        call.function.name
                    )),
                });
            }
        }
    }
}
