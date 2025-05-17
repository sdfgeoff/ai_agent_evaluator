use super::llm_client::LLMClient;
use super::tool_manager::ToolManager;
use agent_types::FinishReason;
use agent_types::llm_types::{Message, ToolDefinition, ToolFunction, ToolFunctionType};
use log::{info, warn};

pub struct Agent {
    llm_client: LLMClient,
    tool_manager: ToolManager,
    pub messages: Vec<Message>,
    task_complete_tool: ToolDefinition,
}

impl Agent {
    pub fn new(llm_client: LLMClient, tool_manager: ToolManager) -> Self {
        Self {
            llm_client,
            tool_manager,
            messages: Vec::new(),

            task_complete_tool: ToolDefinition {
                type_: ToolFunctionType::Function,
                function: ToolFunction {
                    name: "task_complete".to_string(),
                    description: Some("Call when there is nothing more to do on this task, either because it's done or because the task is not possible.".to_string()),
                    parameters: serde_json::from_str(r#"{
                        "type": "object",
                        "properties": {}
                    }"#).unwrap(),
                }
            },
        }
    }

    pub async fn run(
        &mut self,
        initial_messages: Vec<Message>,
        max_iter: usize,
    ) -> Result<FinishReason, Box<dyn std::error::Error + Send + Sync>> {
        self.messages.clear();
        self.messages.extend(initial_messages);

        for _ in 0..max_iter {
            let mut tools = self.tool_manager.get_tools().await;
            tools.push(self.task_complete_tool.clone());
            info!("querying_llm");
            let chat_response = self
                .llm_client
                .make_request(self.messages.clone(), Some(tools))
                .await?;
            let message = &chat_response.choices[0].message;

            info!("llm_response_received");
            self.messages.push(message.clone());

            let mut stop = None;

            match message {
                Message::Text(text_message) => {
                    if text_message.content.is_empty() {
                        stop = Some(FinishReason::EmptyContent);
                    }
                }
                Message::ToolRequest(tool_request_message) => {
                    let mut results = Vec::new();
                    for call in &tool_request_message.tool_calls {
                        if call.function.name == self.task_complete_tool.function.name {
                            stop = Some(FinishReason::TaskCompleteTool);
                            break;
                        } else {
                            let result = self.tool_manager.call_tool(call.clone()).await;
                            results.push(result);
                        }
                    }
                    self.messages.extend(results);
                }
                Message::ToolResponse(_tool_response_message) => {
                    warn!("surprising_tool_response_from_llm")
                }
            }

            if let Some(reason) = stop {
                info!("task_complete");
                return Ok(reason);
            }
        }

        Ok(FinishReason::IterationLimit(max_iter))
    }
}
