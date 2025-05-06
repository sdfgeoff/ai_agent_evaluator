import structlog
from typing import Awaitable, Callable
from evaluator.provider.openai_types import (
    ToolRequestMessage,
    ToolFunction,
    ToolDefinition,
    Message,
)
from evaluator.tool_manager import ToolManager

log = structlog.get_logger(__name__)
MakeLLMRequest = Callable[[list[Message], list[ToolDefinition]], Awaitable[Message]]


IDLE_TOOL = ToolDefinition(
    type="function",
    function=ToolFunction(
        name="task_complete",
        description="Call when there is nothing more to do to compete the users task",
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

    async def run(
        self, initial_messages: list[Message], max_iter: int = 100
    ) -> list[Message]:
        messages = initial_messages

        for _ in range(max_iter):
            tools = self.tool_manager.get_tools() + [IDLE_TOOL]
            log.info("querying_llm", tools=[t.function.name for t in tools])
            message = await self.make_llm_request(
                messages,
                tools,
            )
            log.info("llm_response_received")

            messages.append(message)

            stop = False
            if isinstance(message, ToolRequestMessage):
                # Do them sequentially so that the LLM get confused by concurrency issues
                results: list[Message] = []
                for call in message.tool_calls:
                    if call.function.name == IDLE_TOOL.function.name:
                        stop = True
                    else:
                        result = await self.tool_manager.call_tool(call)
                        results.append(result)
                messages.extend(results)
            
            if stop:
                log.info("task_complete")
                break

        return messages

        
