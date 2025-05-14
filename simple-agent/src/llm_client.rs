use super::llm_api::client::OpenAiClient;
use super::llm_api::types::{ToolDefinition, Message, ChatResponse, ChatParameters};

pub struct LLMClient {
    open_ai_client: OpenAiClient,
    model: String,
}

impl LLMClient {
    pub fn new(open_ai_client: OpenAiClient, model: String) -> Self {
        LLMClient {
            open_ai_client,
            model,
        }
    }

    pub async fn make_request(
        &self,
        messages: Vec<Message>,
        tools: Option<Vec<ToolDefinition>>,
    ) -> Result<ChatResponse, reqwest::Error> {
        let model = self.model.clone();

        return self
            .open_ai_client
            .v1_chat_completions(ChatParameters {
                model,
                messages,
                tools,
                stream: Some(false),
            })
            .await;
    }
}