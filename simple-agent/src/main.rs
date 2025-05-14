use std::collections::HashMap;

use reqwest::header::AUTHORIZATION;
use serde::{Deserialize, Serialize};
mod llm_api;
use llm_api::{client::OpenAiClient, types::ToolFunctionType};

#[derive(Serialize, Deserialize, Debug)]
struct MyBody {
    origin: String,
}

struct LLMClient {
    open_ai_client: OpenAiClient,
    model: String,
}

impl LLMClient {
    fn new(open_ai_client: OpenAiClient, model: String) -> Self {
        LLMClient {
            open_ai_client,
            model,
        }
    }

    async fn make_request(
        &self,
        messages: Vec<llm_api::types::Message>,
        tools: Option<Vec<llm_api::types::ToolDefinition>>,
    ) -> Result<llm_api::types::ChatResponse, reqwest::Error> {
        let model = self.model.clone();

        return self
            .open_ai_client
            .v1_chat_completions(llm_api::types::ChatParameters {
                model,
                messages,
                tools,
                stream: Some(false),
            })
            .await;
    }
}

fn make_provider(url: String, token: String, model: String) -> LLMClient {
    let mut headers = reqwest::header::HeaderMap::new();
    headers.insert(AUTHORIZATION, token.parse().unwrap());

    let http_client = reqwest::Client::builder()
        .default_headers(headers)
        .build()
        .unwrap();

    let api_client = OpenAiClient::new(url, http_client);
    let llm_client = LLMClient::new(api_client, model);
    return llm_client;
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    // This is where we will setup our HTTP client requests.

    let provider = make_provider(
        "http://192.168.18.10:1234".to_string(),
        "asdfasdfasdf".to_string(),
        "qwen3-0.6b".to_string(),
    );
    let messages = vec![llm_api::types::Message::TextMessage(
        llm_api::types::TextMessage {
            role: llm_api::types::Role::User,
            content: "Hello, how are you?".to_string(),
            images: None,
        },
    )];

    let parameters: HashMap<String, serde_json::Value> = HashMap::from([
        (
            "type".to_string(),
            serde_json::Value::String("object".to_string()),
        ),
        (
            "properties".to_string(),
            serde_json::Value::Object(serde_json::map::Map::new()),
        ),
    ]);
    let tools = Some(vec![llm_api::types::ToolDefinition {
        type_: ToolFunctionType::Function,
        function: llm_api::types::ToolFunction {
            name: "Tool1".to_string(),
            description: Some("This is a test tool".to_string()),
            parameters,
        },
    }]);
    let response = provider.make_request(messages, tools).await;
    match response {
        Ok(res) => {
            println!("Response: {:?}", res);
        }
        Err(e) => {
            eprintln!("Error: {:?}", e);
        }
    }

    Ok(())
}
