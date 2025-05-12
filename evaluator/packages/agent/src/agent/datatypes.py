import datetime
from typing import List, Literal
from pydantic import AwareDatetime, BaseModel
from .provider.openai_types import Message


class ModelProvider(BaseModel):
    name: str
    base_url: str
    token: str
    models: List[str]


class ResultStats(BaseModel):
    run_date: AwareDatetime | None = None
    time_seconds: float
    log: list[Message]


class Result(BaseModel):
    stats: ResultStats
    thumbnail: bytes


Tools = Literal["bash", "create_file"]


class TestParameters(BaseModel):
    name: str
    docker_image: str
    blurb: str
    initial_prompt: str
    thumbnail_command: str

    allowed_tools: list[Tools] = ["bash", "create_file"]


class TestToRun(BaseModel):
    name: str
    test_parameters: TestParameters
    provider: ModelProvider
    model: str
    input_folder: str
    output_folder: str
