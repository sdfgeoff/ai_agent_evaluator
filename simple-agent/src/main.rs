use std::{env};

use datatypes::{ResultStats, TestToRun};
use reqwest::header::AUTHORIZATION;
mod datatypes;
mod llm_api;
mod llm_client;
mod agent;
mod tool_manager;
use llm_client::LLMClient;
use llm_api::{client::OpenAiClient};



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

async fn run_test(test: TestToRun) {
    // This is where we will run the test.
    // For now, we will just return a dummy ResultStats object.

    if let Err(e) = env::set_current_dir(&test.output_folder) {
        eprintln!("Failed to change directory to {}: {:?}", test.output_folder, e);
        std::process::exit(1);
    }

    let provider = make_provider(
        "http://192.168.18.10:1234".to_string(),
        "asdfasdfasdf".to_string(),
        "qwen3-0.6b".to_string(),
    );

    let tool_manager = tool_manager::ToolManager::new(
        vec![]
    );

    let mut agent = agent::Agent::new(provider, tool_manager);

    let start_time = chrono::Utc::now();
    let _result = agent.run(test.test_parameters.initial_prompt, 100).await;
    let end_time = chrono::Utc::now();

    let result_stats = ResultStats {
        run_date: Some(start_time),
        time_seconds: (end_time - start_time).num_seconds() as f64,
        log: agent.messages.clone(),
    };


    // let messages = vec![llm_api::types::Message::TextMessage(
    //     llm_api::types::TextMessage {
    //         role: llm_api::types::Role::User,
    //         content: "Hello, how are you?".to_string(),
    //         images: None,
    //     },
    // )];

    // let parameters: HashMap<String, serde_json::Value> = HashMap::from([
    //     (
    //         "type".to_string(),
    //         serde_json::Value::String("object".to_string()),
    //     ),
    //     (
    //         "properties".to_string(),
    //         serde_json::Value::Object(serde_json::map::Map::new()),
    //     ),
    // ]);
    // let tools = Some(vec![llm_api::types::ToolDefinition {
    //     type_: ToolFunctionType::Function,
    //     function: llm_api::types::ToolFunction {
    //         name: "Tool1".to_string(),
    //         description: Some("This is a test tool".to_string()),
    //         parameters,
    //     },
    // }]);
    // let response = provider.make_request(messages, tools).await;
    // match response {
    //     Ok(res) => {
    //         println!("Response: {:?}", res);
    //     }
    //     Err(e) => {
    //         eprintln!("Error: {:?}", e);
    //     }
    // }

    // let result_stats = ResultStats {
    //     run_date: None,
    //     time_seconds: 0.0,
    //     log: vec![],
    // };

    println!("Test result: {:?}", result_stats);
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    // This is where we will setup our HTTP client requests.

    let test_config_env = env::var("TEST_CONFIG");
    let test_config: Result<TestToRun, serde_json::Error> = match test_config_env {
        Ok(config) => {
            serde_json::from_str(&config)
        }
        Err(_) => {
            let default_config = r#"
            {
                "name": "Test1",
                "test_parameters": {
                    "name": "Test1",
                    "docker_image": "test_image",
                    "blurb": "This is a test",
                    "initial_prompt": [
                        {
                            "role": "user",
                            "content": "Hello, how are you?"
                        }
                    ],
                    "allowed_tools": ["bash", "create_file"]
                },
                "provider": {
                    "name": "OpenAI",
                    "base_url": "http://192.168.18.10:1234",
                    "token": "asdfasdfasdf",
                    "models": ["qwen3-0.6b"]
                },
                "model": "qwen3-0.6b",
                "input_folder": "../input",
                "output_folder": "../outputs/Qwen/qwen3-0.6b/hello_world_html"
        }"#;
            serde_json::from_str(default_config)
        }
    };

    let test_config = match test_config {
        Ok(config) => config,
        Err(e) => {
            eprintln!("Error parsing test config: {:?}", e);
            std::process::exit(1);
        }
    };
    run_test(test_config).await;
    Ok(())
}
