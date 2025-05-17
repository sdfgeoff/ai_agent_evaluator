use agent_types::llm_types::{Message, Role, ToolCall, ToolDefinition, ToolResponseMessage};
use serde_json::Value;
use std::{collections::HashMap, pin::Pin};

use log::info;

pub trait ToolAndCallable {
    fn definition(&self) -> ToolDefinition;
    fn call(
        &self,
        arguments: String,
    ) -> Pin<Box<dyn Future<Output = Result<Value, String>> + Send>>;
}

pub struct ToolManager {
    tools_by_name: HashMap<String, Pin<Box<dyn ToolAndCallable>>>,
    tool_definitions: Vec<ToolDefinition>,
}

impl ToolManager {
    pub fn new() -> Self {
        Self {
            tools_by_name: HashMap::new(),
            tool_definitions: Vec::new(),
        }
    }

    pub fn add_tool(&mut self, tool: Pin<Box<dyn ToolAndCallable>>) {
        let def = tool.definition();
        let name = def.function.name.clone();
        let already_exists = self.tools_by_name.insert(name, tool);
        if already_exists.is_some() {
            panic!("Tool with the same name already exists");
        }
        self.tool_definitions.push(def);
    }

    pub async fn get_tools(&self) -> Vec<ToolDefinition> {
        self.tool_definitions.clone()
    }

    pub async fn call_tool(&self, call: ToolCall) -> Message {
        let arguments = call.function.arguments;
        let tool = self.tools_by_name.get(&call.function.name);

        let content = match tool {
            Some(tool) => {
                info!("Calling tool: {}", call.function.name);
                let res = tokio::time::timeout(std::time::Duration::from_secs(60), tool.call(arguments)).await;
                match res {
                    Ok(Ok(result)) => result,
                    Ok(Err(err)) => Value::String(format!("ERROR: {}", err)),
                    Err(elapsed) => Value::String(format!("ERROR: Timeout after {:?}", elapsed))
                }
            }
            None => Value::String(format!("ERROR: Tool `{}` not found", call.function.name)),
        };

        Message::ToolResponse(ToolResponseMessage {
            tool_call_id: call.id,
            role: Role::Tool,
            name: call.function.name.clone(),
            content: content,
        })
    }
}
