from pydantic import BaseModel
from typing import Any, List, Literal, Optional
import mcp.types as types


class ToolFunctionCall(BaseModel):
    name: str
    arguments: str


class ToolCall(BaseModel):
    id: str
    type: Literal["function"]
    function: ToolFunctionCall


class TextMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    images: Optional[List[str]] = None


class ToolRequestMessage(BaseModel):
    role: Literal["assistant"]
    tool_calls: list[ToolCall]


class ToolResponseMessage(BaseModel):
    tool_call_id: str
    role: Literal["tool"]
    name: str
    content: str | list[types.TextContent | types.ImageContent | types.EmbeddedResource]


class ToolFunction(BaseModel):
    name: str
    description: str | None
    parameters: dict[str, Any]


class ToolDefinition(BaseModel):
    type: Literal["function"]
    function: ToolFunction


Message = TextMessage | ToolRequestMessage | ToolResponseMessage


class ChatParameters(BaseModel):
    model: str
    messages: List[Message]
    tools: Optional[List[ToolDefinition]] = None

    stream: Optional[bool]


class MessageChoice(BaseModel):
    index: int
    message: Message
    finish_reason: Optional[str] = None


class ChatResponse(BaseModel):
    choices: List[MessageChoice]


class MessageChoicePartial(BaseModel):
    index: int
    delta: Message
    logprobs: Optional[None] = None
    finish_reason: Optional[Literal["stop"]] = None


class PartialChatCompletion(BaseModel):
    """
    {
        "id":"chatcmpl-160c39e6qb3fdo4yj0rm7",
        "object":"chat.completion.chunk",
        "created":1744024035,
        "model":"qwen2.5-7b-instruct-1m",
        "system_fingerprint":"qwen2.5-7b-instruct-1m",
        "choices":[
            {
                "index":0,
                "delta":{
                    "role":"assistant","content":"It"
                },
                "logprobs":null,
                "finish_reason":null
            }
        ]
    }
    """

    id: str
    object: Literal["chat.completion.chunk"]
    created: int
    model: str
    system_fingerprint: str
    choices: List[MessageChoicePartial]
