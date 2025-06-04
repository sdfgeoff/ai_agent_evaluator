import type React from "react";

export const Tags: React.FC<{
    tags: string[];
}> = ({ tags }) => {
    return (
        <div className="d-flex gap-1">
            {tags.map((tag, index) => (
                <div key={index} className="tag">
                    {tag}
                </div>
            ))}
        </div>
    );
};
