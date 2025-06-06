import React from "react";
import RunCard, { Card } from "./run_card";
import type { TestSummary } from "./models";
import { Tags } from "./Tags";

interface TestContainerProps {
    testName: string;
    tests: TestSummary[];
}


const TestContainer: React.FC<TestContainerProps> = ({
    testName,
    tests,
}) => {
    const byProvider: Record<string, TestSummary[]> = tests.reduce(
        (acc, run) => {
            const providerName = run.provider;
            if (!acc[providerName]) {
                acc[providerName] = [];
            }
            acc[providerName].push(run);
            return acc;
        },
        {} as Record<string, TestSummary[]>
    );

    const providerNames = Object.keys(byProvider).sort();

    return (
        <div id={`test-${testName}`}>
            <div className="panel padding-2">
                <a href={`#${testName}`} className="no-link-underline">
                    <h2>{tests[0].test_metadata.name}</h2>
                </a>
                <Tags tags={tests[0].test_metadata.tags} />
            </div>
            <div className="panel-light padding-x-2 padding-y-1">
                <p>{tests[0].test_metadata.blurb}</p>
            </div>
            <div className="padding-2">
                <div className="flex-wrap d-flex gap-2">
                    {tests.map((run, index) => (
                        <Card key={index} title={`${run.provider} - ${run.model_key}`} image={`test_results/${run.output_folder}/index.png`} link={`?view_test=${run.output_folder}`} />
                    ))}
                </div>
            </div>
        </div>
    );
};

export default TestContainer;