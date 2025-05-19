import React from "react";
import type { TestSummary } from "./models";

interface RunCardProps {
    run: TestSummary
}

const RunCard: React.FC<RunCardProps> = ({ run }) => {
    return (
        <div className="run_card">
            <h4>{run.model_key}</h4>
            <div className="zoom-outer">
                <div className="zoom-inner">
                    <iframe
                        src={`test_results/${run.output_folder}/index.html`}
                        width="1920"
                        height="1080"
                        title="Run Output"
                    ></iframe>
                </div>
            </div>
            <div className="d-flex">
                <div>
                    <a href={`test_results/${run.output_folder}/index.html`}>Fullscreen</a>
                </div>
                <div className="flex-grow-1"></div>
                <div>
                    <a href={`test_results/${run.output_folder}/log.html`}>Message Log</a>
                </div>
            </div>
        </div>
    );
};

export default RunCard;
