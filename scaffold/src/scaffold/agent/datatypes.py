import datetime
from typing import List, Literal
from pydantic import AwareDatetime, BaseModel
from .provider.openai_types import Message

class Model(BaseModel):
    key: str
    enabled: bool

class ModelProvider(BaseModel):
    name: str
    base_url: str
    token_env_var: str | None = None
    models: List[Model]
    enable: bool = True


class ResultStats(BaseModel):
    run_date: AwareDatetime | None = None
    time_seconds: float
    log: list[Message]


class Result(BaseModel):
    stats: ResultStats


Tools = Literal["bash", "create_file"]




class TestParameters(BaseModel):
    docker_image: str
    initial_prompt: list[Message]
    allowed_tools: list[Tools] = ["bash", "create_file"]


class TestConfig(TestParameters):
    name: str
    blurb: str
    tags: list[str] = []



class TestToRun(BaseModel):
    name: str
    test_parameters: TestConfig
    provider: ModelProvider
    model: Model
    input_folder: str
    output_folder: str
    enable: bool = True
