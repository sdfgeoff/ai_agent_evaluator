from typing import List

from pydantic import BaseModel
from agent.agent.datatypes import ModelProvider


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

            ],
        ),
    ]

    test_input_directory: str = "/home/geoffrey/Projects/ai-agent-evaluator/inputs"
    test_output_directory: str = "/home/geoffrey/Projects/ai-agent-evaluator/outputs"


def get_config() -> Config:
    return Config()
