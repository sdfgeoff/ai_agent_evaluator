# import os
import os
from typing import List

from pydantic import BaseModel
from agent.datatypes import ModelProvider


class Config(BaseModel):
    providers: List[ModelProvider] = [
        ModelProvider(
            name="Qwen",
            base_url="http://192.168.18.10:1234",
            token="asdf",
            models=[
                "qwen3-0.6b",
                "qwen3-4b",
                "qwen3-30b-a3b",
                "qwen-3-32b",
                "qwen2.5-14b-instruct",
                "qwen2.5-7b-instruct-1m",
            ],
        ),
        # ModelProvider(
        #     name="THUDM",
        #     base_url="http://192.168.18.10:1234",
        #     token="asdf",
        #     models=[
        #         "glm-4-9b-0414",
        #     ],
        # ),
        ModelProvider(
            name="QWQ",
            base_url="http://192.168.18.10:1234",
            token="asdf",
            models=[
                "qwq-32b",
            ],
        ),
        ModelProvider(
            name="Meta",
            base_url="http://192.168.18.10:1234",
            token="asdf",
            models=[
                "meta-llama-3.1-8b-instruct",
            ],
        ),
        ModelProvider(
            name="OpenAI",
            base_url="https://api.openai.com",
            token=os.getenv("OPENAI_API_KEY", ""),
            models=[
                "o4-mini",
                "o3-mini",
            ],
        ),
    ]

    test_input_directory: str = "/home/geoffrey/Projects/ai-agent-evaluator/inputs"
    test_output_directory: str = "/home/geoffrey/Projects/ai-agent-evaluator/outputs"


def get_config() -> Config:
    return Config()
