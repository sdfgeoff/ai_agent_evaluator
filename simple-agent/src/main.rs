use reqwest::header::AUTHORIZATION;
use serde::{Deserialize, Serialize};
mod llm_api;
use llm_api::client::OpenAiClient;

#[derive(Serialize, Deserialize, Debug)]
struct MyBody {
    origin: String,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    // This is where we will setup our HTTP client requests.

    let mut headers = reqwest::header::HeaderMap::new();
    headers.insert(AUTHORIZATION, "asdf".parse().unwrap());

    let http_client = reqwest::Client::builder()
        .default_headers(headers)
        .build()?;

    let llm_client = OpenAiClient::new("https://api.openai.com/".to_string(), http_client);

    let llm_request = llm_api::types::ChatParameters {
        model: "gpt-3.5-turbo".to_string(),
        messages: vec![llm_api::types::Message::TextMessage(
            llm_api::types::TextMessage {
                role: llm_api::types::Role::User,
                content: "Hello, how are you?".to_string(),
                images: None,
            },
        )],
        tools: Some(vec![]),
        stream: Some(false),
    };

    let res = llm_client.v1_chat_completions(llm_request).await?;

    println!("Deserialized response: {:?}", res);

    Ok(())
}
