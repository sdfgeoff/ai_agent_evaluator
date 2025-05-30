import type { Message } from "./llm_models";

export interface TestMetadata {
    name: string;
    blurb: string;
    tags: string[];
}

export interface TestSummary {
    test_metadata: TestMetadata;
    provider: string;
    model_key: string;
    output_folder: string;
    run_date?: string; // Use ISO 8601 string for DateTime<Utc>
    finish_reason?: string;
}

export interface Summary {
    tests: TestSummary[];
}



export interface RunStats {
   run_date?: string,
   time_seconds: number,
   log: Message[],
   finish_reason: any,
}


export interface TestConfig extends TestMetadata {
    docker_image: string,
    initial_prompt:Message[],
    allowed_tools: string[],
}

export interface TestToRun {
    name: string,
    test_parameters: TestConfig,
    provider: ModelProvider,
    model: Model,
    input_folder: string,
    output_folder: string,
};

export interface Model {
    key: string;
    enabled: boolean;
}
export interface ModelProvider {
    name: string,
    base_url: string,
    token_env_var?: string,
    models: Model[],
    enabled: boolean,
}
