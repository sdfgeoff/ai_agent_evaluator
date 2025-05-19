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

