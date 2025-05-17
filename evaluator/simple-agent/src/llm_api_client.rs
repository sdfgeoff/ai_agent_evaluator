use agent_types::llm_types::{ChatParameters, ChatResponse};
use log::{warn};

pub struct OpenAiClient {
    client: reqwest::Client,
    base_url: String,
}

impl OpenAiClient {
    pub fn new(base_url: String, client: reqwest::Client) -> Self {
        Self { client, base_url }
    }

    pub async fn v1_chat_completions(
        &self,
        llm_request: ChatParameters,
    ) -> Result<ChatResponse, reqwest::Error> {
        let url = format!("{}/v1/chat/completions", self.base_url);
        let raw = self
            .client
            .post(&url)
            .header("Content-Type", "application/json")
            .json(&llm_request)
            .send()
            .await?;

        let result = raw.error_for_status_ref().err();
        if let Some(err) = result {
            warn!("STATUS CODE NOT OK: {:?}", raw.text().await?);
            return Err(err);
        }
        raw.json::<ChatResponse>().await
    }
}
