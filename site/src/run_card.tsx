import React from "react";
import type { TestSummary } from "./models";


interface CardProps {
    title: string;
    image: string;
    link: string;
    
}

export const Card : React.FC<CardProps> = ({ title, image, link }) => {
    return (
        <a className="run_card no-link-underline rounded-1 hover-bg-panel padding-0_5" style={{
            width: "240px",
            height: "160px",
            display: 'block',
            overflow: 'hidden',
        }} href={link} title={title}>
            <div className="text-center font-weight-bold padding-1" style={{
                overflow: 'ellipsis',
                whiteSpace: 'nowrap',
            }}>
                {title}
            </div>
                <img
                    src={image}
                    style={{
                        objectFit: 'contain',
                        maxWidth: '100%',
                        maxHeight: '100%',
                    }}

                />
            </a>
    );
}

interface RunCardProps {
    run: TestSummary
}

const RunCard: React.FC<RunCardProps> = ({ run }) => {
    const html_url = `test_results/${run.output_folder}/index.html`;
    return (
        <div className="run_card">
            <h4>{run.model_key}</h4>
            <a href={html_url}>
            <img
                src={`test_results/${run.output_folder}/index.png`}
                width="240"
                height="135"
                title="Screenshot of the output"
            />
            </a>
            <div className="d-flex">
                <div>
                    <a href={html_url}>View Site</a>
                </div>
                <div className="flex-grow-1"></div>
                <div>
                    <a href={`?view_test=${run.output_folder}`}>View Details</a>
                </div>
            </div>
        </div>
    );
};

export default RunCard;
