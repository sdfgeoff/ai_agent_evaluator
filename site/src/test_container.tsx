import React from "react";
import RunCard from "./run_card";
import type { TestSummary } from "./models";

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
        <div id={`test-${testName}`} className="">
            <div className="panel">
                <a href={`#${testName}`} className="no-link-underline">
                    <h2>{tests[0].test_metadata.name}</h2>
                </a>
                <div className="d-flex gap-1">
                    {tests[0].test_metadata.tags.map((tag, index) => (
                        <div key={index} className="tag">
                            {tag}
                        </div>
                    ))}
                </div>
            </div>
            <div className="panel-light">
                <p>{tests[0].test_metadata.blurb}</p>
                {/* <h3>Initial Prompt:</h3>
                {tests[0].test_metadata.initialPrompt.map((prompt, index) => (
                    <pre key={index} className="prompt">
                        {prompt.content}
                    </pre>
                ))} */}
            </div>
            {providerNames.map((provider) => {
                const providerTests = byProvider[provider].sort(
                    (a, b) => a.model_key.localeCompare(b.model_key)
                );
                return (
                    <React.Fragment key={provider}>
                        <h3>{provider}</h3>
                        <div className="run_container padding-1 d-flex gap-1">
                            {providerTests.map((run, index) => (
                                <RunCard key={index} run={run} />
                            ))}
                        </div>
                    </React.Fragment>
                );
            })}
        </div>
    );
};

export default TestContainer;