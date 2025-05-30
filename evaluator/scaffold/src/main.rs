use agent_types::{FinishReason, ModelProvider, ResultStats, TestConfig, TestMetadata, TestToRun};
use log::error;
use serde::{Deserialize, Serialize};
use std::collections::HashSet;
use std::fs;
use std::path::{Path, PathBuf};
use structopt::StructOpt;
mod run_test_case;
use run_test_case::run_test;
use structured_logger::Builder;
use chrono::{Date, DateTime, Utc};


#[derive(Debug, StructOpt)]
struct Args {
    #[structopt(long, help = "Path to the agent binary")]
    agent_binary: String,

    #[structopt(long, help = "Path to the llm_providers config file")]
    llm_providers_config: String,

    #[structopt(
        long,
        help = "Path to the test input directory",
        default_value = "inputs"
    )]
    input_directory: String,

    #[structopt(
        long,
        help = "Path to the test output directory",
        default_value = "outputs"
    )]
    output_directory: String,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct ProviderConfig {
    pub providers: Vec<ModelProvider>,
}

fn load_config(file_path: &Path) -> TestConfig {
    let file_content = fs::read_to_string(file_path).expect("Failed to read config file");
    serde_json::from_str(&file_content).expect("Failed to parse config file")
}

fn convert_to_absolute_path_quitting_if_error(path: &str) -> PathBuf {
    let absolute_path = fs::canonicalize(path);
    match absolute_path {
        Ok(path) => path,
        Err(_) => {
            eprintln!("Error: Failed to resolve path: {}", path);
            std::process::exit(1);
        }
    }
}

fn check_if_test_needs_rerun(test: &TestToRun) -> bool {
    let existing_config_file = Path::new(&test.output_folder).join("config.json");

    if existing_config_file.exists() {
        let existing_config = fs::read_to_string(&existing_config_file).unwrap();
        let new_config =
            fs::read_to_string(Path::new(&test.input_folder).join("config.json")).unwrap();

        // Parse both configs
        let existing_config: TestConfig = serde_json::from_str(&existing_config).unwrap();
        let new_config: TestConfig = serde_json::from_str(&new_config).unwrap();

        existing_config.test_parameters != new_config.test_parameters
    } else {
        true
    }
}

#[derive(Serialize, Deserialize, Debug)]
struct TestSummary {
    test_metadata: TestMetadata,
    
    provider: String,
    model_key: String,

    output_folder: String,

    run_date: Option<DateTime<Utc>>,
    finish_reason: Option<FinishReason>,
}

#[derive(Serialize, Deserialize, Debug)]
struct Summary {
    tests: Vec<TestSummary>,
}

fn generate_test_summary(
    output_directory: &PathBuf,
    test: &TestToRun,
) -> TestSummary {

    // Load result stats from the test output folder
    let stats_file = Path::new(&test.output_folder)
        .join("stats.json");
    let stats_content = fs::read_to_string(stats_file)
        .ok();

    let parse = |content: String| {
        serde_json::from_str::<ResultStats>(&content)
            .expect("Failed to parse stats file")
    };
    let stats: Option<ResultStats> = stats_content.map(parse);

    let run_date: Option<DateTime<Utc>> = stats
        .as_ref()
        .and_then(|s| s.run_date);
    let finish_reason: Option<FinishReason> = stats
        .as_ref()
        .and_then(|s| s.finish_reason.clone());

    TestSummary {
        test_metadata: test.test_parameters.metadata.clone(),
        provider: test.provider.name.clone(),
        model_key: test.model.key.clone(),
        output_folder: Path::new(&test.output_folder)
            .strip_prefix(output_directory)
            .unwrap()
            .to_string_lossy()
            .to_string(),
        run_date,
        finish_reason,
    }
}

fn main() {
    Builder::with_level("info")
        // .with_target_writer("*", new_writer(tokio::io::stdout()))
        .init();

    let args = Args::from_args();

    let input_directory = convert_to_absolute_path_quitting_if_error(&args.input_directory);
    let output_directory = convert_to_absolute_path_quitting_if_error(&args.output_directory);
    let agent_binary = convert_to_absolute_path_quitting_if_error(&args.agent_binary);

    let test_folders = fs::read_dir(input_directory).expect("Failed to read input directory");

    let mut all_tests = Vec::new();
    let mut test_names = HashSet::new();

    // Parse the provider config json file
    let provider_config_file =
        convert_to_absolute_path_quitting_if_error(&args.llm_providers_config);
    let provider_config_content =
        fs::read_to_string(provider_config_file).expect("Failed to read provider config file");
    let provider_config: ProviderConfig = serde_json::from_str(&provider_config_content)
        .expect("Failed to parse provider config file");
    let providers = provider_config.providers;

    for entry in test_folders {
        let entry = entry.expect("Failed to read directory entry");
        let test_folder = entry.path();
        let test_settings_file = test_folder.join("config.json");

        if !test_settings_file.exists() {
            error!(
                "Test config not found for folder: {:?}, file: {:?}",
                test_folder, test_settings_file
            );
            continue;
        }

        // info!(test_file=test_settings_file.to_str(); "found_test");
        let test_parameters = load_config(&test_settings_file);

        if !test_names.insert(test_parameters.metadata.name.clone()) {
            panic!("Duplicate test name: {}", test_parameters.metadata.name);
        }

        for provider in &providers {
            for model in &provider.models {
                let output_folder = output_directory
                    .join(provider.name.clone())
                    .join(model.key.clone())
                    .join(test_folder.file_name().unwrap());

                all_tests.push(TestToRun {
                    name: test_folder
                        .file_name()
                        .unwrap()
                        .to_string_lossy()
                        .to_string(),
                    test_parameters: test_parameters.clone(),
                    provider: provider.clone(),
                    model: model.clone(),
                    input_folder: test_folder.to_string_lossy().to_string(),
                    output_folder: output_folder.to_string_lossy().to_string(),
                });
            }
        }
    }

    all_tests.sort_by(|a, b| {
        a.provider
            .name
            .cmp(&b.provider.name)
            .then(a.model.key.cmp(&b.model.key))
    });
    let mut tests_to_run = all_tests.clone();
    // Remove any with the provider disabled
    tests_to_run.retain(|test| test.provider.enabled);
    // Remove any with the model disabled
    tests_to_run.retain(|test| test.model.enabled);


    for test in &tests_to_run {
        let test_needs_rerun = check_if_test_needs_rerun(test);

        if test_needs_rerun {
            if let Err(e) = run_test(agent_binary.clone(), test) {
                error!(
                    "Test failed for provider: {}, model: {}, test folder: {:?}, error: {:?}",
                    test.provider.name, test.model.key, test.input_folder, e
                );
            }
        }
        // Write the test-to-run result to the output folder
        let test_file = std::fs::File::create(format!("{}/test.json", test.output_folder)).unwrap();
        let test_writer = std::io::BufWriter::new(test_file);
        serde_json::to_writer_pretty(test_writer, &test).unwrap();
    }

    // Generate a summary of the tests.
    let summary = Summary {
        tests: tests_to_run
            .iter()
            .map(
                |test| generate_test_summary(&output_directory, &test),
            )
            .collect(),
    };
    // Write the summary to a json file
    let summary_file = std::fs::File::create(output_directory.join("summary.json")).unwrap();
    let summary_writer = std::io::BufWriter::new(summary_file);
    serde_json::to_writer_pretty(summary_writer, &summary).unwrap();

}
