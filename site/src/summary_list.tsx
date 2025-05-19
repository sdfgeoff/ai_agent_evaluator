import React, { useState } from "react";
import TestContainer from "./test_container";
import type { TestSummary } from "./models";

interface SummaryProps {
    tests: TestSummary[];
}

const SummaryList: React.FC<SummaryProps> = ({ tests }) => {
    const [tagFilter, setTagFilter] = useState("");
    const [providerFilter, setProviderFilter] = useState("");
    const [modelKeyFilter, setModelKeyFilter] = useState("");

    // Extract unique tags from the tests
    const uniqueTags = Array.from(
        new Set(tests.flatMap((test) => test.test_metadata.tags))
    );

    // Extract unique providers from the tests
    const uniqueProviders = Array.from(
        new Set(tests.map((test) => test.provider))
    );

    // Extract unique model keys based on the selected provider
    const uniqueModelKeys = Array.from(
        new Set(
            tests
                .filter((test) =>
                    providerFilter ? test.provider === providerFilter : true
                )
                .map((test) => test.model_key)
        )
    );

    const filteredTests = tests.filter((test) => {
        const matchesTag = tagFilter ? test.test_metadata.tags.includes(tagFilter) : true;
        const matchesProvider = providerFilter
            ? test.provider === providerFilter
            : true;
        const matchesModelKey = modelKeyFilter
            ? test.model_key === modelKeyFilter
            : true;
        return matchesTag && matchesProvider && matchesModelKey;
    });

    const byTestName: Record<string, TestSummary[]> = filteredTests.reduce(
        (acc, test) => {
            const testName = test.test_metadata.name;
            if (!acc[testName]) {
                acc[testName] = [];
            }
            acc[testName].push(test);
            return acc;
        },
        {} as Record<string, TestSummary[]>
    );

    const testNames = Object.keys(byTestName).sort();

    return (
        <>
            <h2>Filters</h2>
            <div>
                <label>
                    Tag:
                    <select
                        value={tagFilter}
                        onChange={(e) => setTagFilter(e.target.value)}
                    >
                        <option value="">All</option>
                        {uniqueTags.map((tag) => (
                            <option key={tag} value={tag}>
                                {tag}
                            </option>
                        ))}
                    </select>
                </label>
                <label>
                    Provider:
                    <select
                        value={providerFilter}
                        onChange={(e) => {
                            setProviderFilter(e.target.value);
                            setModelKeyFilter(""); // Reset model key filter when provider changes
                        }}
                    >
                        <option value="">All</option>
                        {uniqueProviders.map((provider) => (
                            <option key={provider} value={provider}>
                                {provider}
                            </option>
                        ))}
                    </select>
                </label>
                <label>
                    Model Key:
                    <select
                        value={modelKeyFilter}
                        onChange={(e) => setModelKeyFilter(e.target.value)}
                    >
                        <option value="">All</option>
                        {uniqueModelKeys.map((modelKey) => (
                            <option key={modelKey} value={modelKey}>
                                {modelKey}
                            </option>
                        ))}
                    </select>
                </label>
            </div>
            <h2>Table of Contents</h2>
            <ul>
                {testNames.map((testName) => {
                    const testConfig = byTestName[testName][0].test_metadata;
                    return (
                        <li key={testName}>
                            <a href={`#test-${testName}`}>{testConfig.name}</a>
                        </li>
                    );
                })}
            </ul>
            <h1>Results</h1>
            {testNames.map((testName) => (
                <TestContainer
                    key={testName}
                    testName={testName}
                    tests={byTestName[testName]}
                />
            ))}
        </>
    );
};

export default SummaryList;