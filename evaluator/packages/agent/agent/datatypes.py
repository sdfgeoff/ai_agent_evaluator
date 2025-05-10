from typing import List
from pydantic import BaseModel
from .provider.openai_types import Message


class ModelProvider(BaseModel):
    name: str
    base_url: str
    token: str
    models: List[str]


class ResultStats(BaseModel):
    time_seconds: float
    log: list[Message]


class Result(BaseModel):
    stats: ResultStats
    thumbnail: bytes


class TestParameters(BaseModel):
    name: str
    docker_image: str
    blurb: str
    initial_prompt: str
    thumbnail_command: str


class TestToRun(BaseModel):
    name: str
    test_parameters: TestParameters
    provider: ModelProvider
    model: str
    input_folder: str
    output_folder: str
