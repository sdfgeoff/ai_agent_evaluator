use crate::llm_api::types::{
    ToolDefinition, ToolCall, Message,
};


pub struct ToolAndcallable {
    pub tool: ToolDefinition,
    pub callable: Box<dyn Fn(ToolCall) -> Message + Send + Sync>,
}

pub struct ToolManager {
    tools: Vec<ToolAndcallable>,
}

impl ToolManager {
    pub fn new(extra_tools: Vec<ToolAndcallable>) -> Self {
        Self {
            tools: extra_tools,
        }
    }

    pub async fn get_tools(&self) -> Vec<ToolDefinition> {
        let mut tools = Vec::new();
        for tool in &self.tools {
            tools.push(tool.tool.clone());
        }
        tools
    }
    pub async fn call_tool(&self, call: ToolCall) -> Message {
        unimplemented!()
    }
}

