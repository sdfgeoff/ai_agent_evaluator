import structlog
from typing import Awaitable, Callable
from .provider.openai_types import (
    ToolRequestMessage,
    ToolFunction,
    ToolDefinition,
    Message,
)
from .tool_manager import ToolManager

log = structlog.get_logger(__name__)
MakeLLMRequest = Callable[[list[Message], list[ToolDefinition]], Awaitable[Message]]


TASK_COMPLETE_TOOL = ToolDefinition(
    type="function",
    function=ToolFunction(
        name="task_complete",
        description="Call when there is nothing more to do on this task, either because it's done or because because the task is not possible.",
        parameters={
            "type": "object",
            "properties": {},
        },
    ),
)


class Agent:
    def __init__(self, make_llm_request: MakeLLMRequest, tool_manager: ToolManager):
        self.make_llm_request = make_llm_request
        self.tool_manager = tool_manager

        self.messages: list[Message] = []

    async def run(
        self, initial_messages: list[Message], max_iter: int = 100
    ):
        self.messages = initial_messages

        for _ in range(max_iter):
            tools = self.tool_manager.get_tools() + [TASK_COMPLETE_TOOL]
            log.info("querying_llm", tools=[t.function.name for t in tools])
            message = await self.make_llm_request(
                self.messages,
                tools,
            )
            log.info("llm_response_received")

            self.messages.append(message)

            stop = None
            if isinstance(message, ToolRequestMessage):
                # Do them sequentially so that the LLM get confused by concurrency issues
                results: list[Message] = []
                for call in message.tool_calls:
                    if call.function.name == TASK_COMPLETE_TOOL.function.name:
                        stop = 'stop_tool'
                        break
                    else:
                        result = await self.tool_manager.call_tool(call)
                        results.append(result)

                self.messages.extend(results)
            else:
                if message.content == "":
                    # No content, we are probably done
                    stop = 'empty_content'
        
            if stop:
                log.info("task_complete", reason=stop)
                break
