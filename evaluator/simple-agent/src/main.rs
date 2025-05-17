use std::env;

use agent_types::{ResultStats, TestToRun, Tools};
use reqwest::header::AUTHORIZATION;
mod agent;
mod llm_api_client;
mod llm_client;
mod tool_manager;
use llm_api_client::OpenAiClient;
use llm_client::LLMClient;

mod default_tools;

use structured_logger::{Builder, async_json::new_writer};

fn make_provider(url: String, token: String, model: String) -> LLMClient {
    let mut headers = reqwest::header::HeaderMap::new();
    headers.insert(AUTHORIZATION, format!("Bearer {}", token).parse().unwrap());

    let http_client = reqwest::Client::builder()
        .default_headers(headers)
        .build()
        .unwrap();

    let api_client = OpenAiClient::new(url, http_client);
    LLMClient::new(api_client, model)
}

async fn run_test(test: TestToRun) {
    // This is where we will run the test.
    // For now, we will just return a dummy ResultStats object.

    if let Err(e) = env::set_current_dir(&test.output_folder) {
        eprintln!(
            "Failed to change directory to {}: {:?}",
            test.output_folder, e
        );
        std::process::exit(1);
    }

    let provider = make_provider(test.provider.base_url.clone(), test.provider.token.clone(), test.model.key.clone());

    let mut tool_manager = tool_manager::ToolManager::new();
    if test.test_parameters.test_parameters.allowed_tools.contains(&Tools::Bash) {
        let bash_tool = default_tools::BashTool {};
        tool_manager.add_tool(Box::pin(bash_tool));
    }
    if test
        .test_parameters.test_parameters
        .allowed_tools
        .contains(&Tools::CreateFile)
    {
        let create_file_tool = default_tools::CreateFileTool {};
        tool_manager.add_tool(Box::pin(create_file_tool));
    }

    let mut agent = agent::Agent::new(provider, tool_manager);

    let start_time = chrono::Utc::now();
    let result = agent.run(test.test_parameters.test_parameters.initial_prompt.clone(), 100).await;
    let end_time = chrono::Utc::now();

    if result.is_err() {
        eprintln!("Error running test: {:?}", result);
        std::process::exit(1);
    }

    let result_stats = ResultStats {
        run_date: Some(start_time),
        time_seconds: (end_time - start_time).num_seconds() as f64,
        log: agent.messages.clone(),
        finish_reason: result.ok(),
    };

    // Write stats to stats.json in the output folder
    let stats_file = std::fs::File::create(format!("{}/stats.json", test.output_folder)).unwrap();
    let stats_writer = std::io::BufWriter::new(stats_file);
    serde_json::to_writer(stats_writer, &result_stats).unwrap();
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    // This is where we will setup our HTTP client requests.
    Builder::with_level("info")
        .with_target_writer("*", new_writer(tokio::io::stdout()))
        .init();

    let test_config_env = env::var("TEST_CONFIG");
    let test_config: Result<TestToRun, serde_json::Error> = match test_config_env {
        Ok(config) => serde_json::from_str(&config),
        Err(_) => {
            let default_config = r#"
            {
                "name": "Test1",
                "test_parameters": {
                    "name": "Hello World",
                    "docker_image": "test_image",
                    "blurb": "This is a test",
                    "initial_prompt": [
                        {
                            "role": "user",
                            "content": "Creae a hello world HTML file using the bash tool"
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
