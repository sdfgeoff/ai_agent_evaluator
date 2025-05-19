use std::{collections::HashMap, fs};
use std::process::Command;
use std::path::Path;
use log::{info, warn};
use agent_types::TestToRun;
use std::path::PathBuf;

pub fn run_test(agent_binary: PathBuf, test: &TestToRun) -> Result<(), String> {
    info!(
        provider=test.provider.name,
        model=test.model.key,
        input_folder=test.input_folder;
        "starting_test",
    );

    // Set up environment
    fs::create_dir_all(&test.output_folder).expect("Failed to create output folder");
    let options = fs_extra::dir::CopyOptions {
        overwrite: true,
        skip_exist: false,
        copy_inside: true,
        content_only: true,
        ..Default::default()
    };
    fs_extra::dir::copy(&test.input_folder, &test.output_folder, &options)
        .expect("Failed to copy input folder to output folder");

    // Spin up docker container
    let name = format!("{}_{}_{}", test.name, test.provider.name, test.model.key);
    let docker_name: String = name.chars().filter(|c| c.is_alphanumeric() || *c == '_' || *c == '-').collect();
    let agent_folder = Path::new(&agent_binary).parent().unwrap();

    info!(
        docker_name,
        docker_image=test.test_parameters.test_parameters.docker_image;
        "start_container",
    );

    // Map paths for Docker
    let local_test_config = TestToRun {
        name: test.name.clone(),
        test_parameters: test.test_parameters.clone(),
        provider: test.provider.clone(),
        model: test.model.clone(),
        input_folder: "/project".to_string(),
        output_folder: "/project".to_string(),
    };

    let mut env_vars = HashMap::new();
    env_vars.insert("TEST_CONFIG", serde_json::to_string(&local_test_config).expect("Failed to serialize test config"));
    match test.provider.token_env_var {
        Some(ref token_env_var) => {
            env_vars.insert(token_env_var, std::env::var(token_env_var).map_err(|_| {
                format!("Environment variable {} not set", token_env_var)
            }).expect("Failed to get environment variable"));
        }
        None => {}
    }
  
    let volumes = vec![
        format!("{}:/project:rw", test.output_folder),
        format!("{}:/agent:ro", agent_folder.to_string_lossy()),
    ];

    let mut args: Vec<String> = Vec::new();

    args.push("run".to_string());
    args.push("--rm".to_string());
    
    for volume in volumes {
        args.push("-v".to_string());
        args.push(volume);
    }
    args.push("-w".to_string());
    args.push("/agent".to_string());
    for (key, value) in env_vars {
        args.push("-e".to_string());
        args.push(format!("{}={}", key, value));
    }
    args.push("--name".to_string());
    args.push(docker_name.clone());
    args.push(test.test_parameters.test_parameters.docker_image.clone());
    args.push(format!("/agent/{}", Path::new(&agent_binary).file_name().unwrap().to_string_lossy()));

    let process = Command::new("docker")
        .args(&args)
        .spawn()
        .expect("Failed to execute docker command");

    let output = process.wait_with_output().expect("Failed to read stdout");

    if !output.status.success() {
        warn!(
            docker_name,
            docker_image=test.test_parameters.test_parameters.docker_image,
            error=String::from_utf8_lossy(&output.stderr);
            "docker_command_failed"
        );
        return Err(format!(
            "Agent Failed to Run: {}",
            String::from_utf8_lossy(&output.stderr)
        ));
    }
    info!(
        docker_name,
        docker_image=test.test_parameters.test_parameters.docker_image;
        "containter_finished",
    );

    Ok(())
}
