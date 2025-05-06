from typing import List

from pydantic import BaseModel
from evaluator.datatypes import ModelProvider


class Config(BaseModel):
    providers: List[ModelProvider] = [
        ModelProvider(
            name="Qwen",
            base_url="http://localhost:1234",
            token="asdf",
            models=[
                #"qwen3-0.6b",
                "qwen3-4b",
            ],
        ),
    ]

    test_input_directory: str = "inputs"
    test_output_directory: str = "outputs"



def get_config() -> Config:
    return Config()