import type React from "react";

export const Tags: React.FC<{
    tags: string[];
}> = ({ tags }) => {
    return (
        <div className="d-flex gap-1">
            {tags.map((tag, index) => (
                <div key={index} className="tag padding-y-0_5 padding-x-1 rounded-1">
                    {tag}
                </div>
            ))}
        </div>
    );
};
