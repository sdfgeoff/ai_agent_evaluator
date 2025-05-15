use std::collections::HashMap;
use crate::llm_api::types::{Message, Role, ToolCall, ToolDefinition, ToolResponseMessage};
use serde_json::Value;

use log::{info};

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
        info!("Loaded {} tools", tool_definitions.len());

        Self {
            tools_by_name,
            tool_definitions,
        }
    }

    pub async fn get_tools(&self) -> Vec<ToolDefinition> {
        self.tool_definitions.clone()
    }

    pub async fn call_tool(&self, call: ToolCall) -> Message {
        let arguments = call.function.arguments;
        let tool = self.tools_by_name.get(&call.function.name);

        match tool {
            Some(tool) => {
                let res = tool.call(arguments);

                match res {
                    Ok(res) => Message::ToolResponse(ToolResponseMessage {
                        tool_call_id: call.id,
                        role: Role::Tool,
                        name: call.function.name.clone(),
                        content: res,
                    }),
                    Err(err) => Message::ToolResponse(ToolResponseMessage {
                        tool_call_id: call.id,
                        role: Role::Tool,
                        name: call.function.name.clone(),
                        content: Value::String(format!("ERROR: {}", err)),
                    }),
                }
            }
            None => Message::ToolResponse(ToolResponseMessage {
                tool_call_id: call.id,
                role: Role::Tool,
                name: call.function.name.clone(),
                content: Value::String(format!("ERROR: Tool `{}` not found", call.function.name)),
            }),
        }
    }
}
