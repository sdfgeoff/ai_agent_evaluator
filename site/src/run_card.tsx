import React from "react";


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