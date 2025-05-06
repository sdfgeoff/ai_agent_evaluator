from typing import List
from pydantic import BaseModel


class ModelProvider(BaseModel):
    name: str
    base_url: str
    token: str
    models: List[str]


class TestParameters(BaseModel):
    docker_image: str
    blurb: str
    initial_prompt: str
    thumbnail_command: str


class ResultStats(BaseModel):
    time_seconds: float


class Result(BaseModel):
    stats: ResultStats
    thumbnail: bytes
    log: str




class TestToRun(BaseModel):
    name: str
    test_parameters: TestParameters
    provider: ModelProvider
    model: str
    test_folder: str