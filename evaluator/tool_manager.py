from typing import Any, Awaitable, Callable, NamedTuple
import structlog
import mcp.types as types
from evaluator.mcp_manager import MCPManager
from evaluator.provider.openai_types import Message, ToolCall, ToolDefinition, ToolFunction, ToolResponseMessage
import json

log = structlog.get_logger(__name__)

class Tool(NamedTuple):
    definition: ToolDefinition
    callable: Callable[[dict[str, Any]], Awaitable[types.CallToolResult]]


def make_callable(mcp_manager: MCPManager, tool_name: str) -> Callable[[dict[str, Any]], Awaitable[types.CallToolResult]]:
    async def callable(args: dict[str, Any]) -> types.CallToolResult:
        return await mcp_manager.call_tool(tool_name, args)

    return callable

class ToolManager:
    def __init__(self, mcp_manager: MCPManager, extra_tools: list[Tool]):
        self.mcp_manager = mcp_manager

        self.tools: list[Tool] = []
        self.tools = [
            Tool(ToolDefinition(
                type="function",
                function=ToolFunction(
                    name=t.name,
                    description=t.description,
                    parameters=t.inputSchema,
                ),
            ), make_callable(self.mcp_manager, t.name))
            for t in self.mcp_manager.get_tools()
        ] + extra_tools

        log.info(
            "tool_manager_initialized",
            tools=[t.definition.function.name for t in self.tools],
        )

    def get_tools(self) -> list[ToolDefinition]:
        return [t.definition for t in self.tools]

    async def call_tool(self, function_call: ToolCall) -> Message:
        # Check tool exists
        functions = [
            t
            for t in self.tools
            if t.definition.function.name == function_call.function.name
        ]
        if len(functions) == 0:
            return ToolResponseMessage(
                tool_call_id=function_call.id,
                role="tool",
                name=function_call.function.name,
                content=f"ERROR: Function {function_call.function.name} not found",
            )
        function = functions[0]

        try:
            args = json.loads(function_call.function.arguments)
        except json.JSONDecodeError as e:
            return ToolResponseMessage(
                tool_call_id=function_call.id,
                role="tool",
                name=function_call.function.name,
                content=f"ERROR: {e}",
            )

        try:
            results = await function.callable(
                args,
            )
        except Exception as e:
            log.error(f"Error calling tool {function_call.function.name}: {e}")
            return ToolResponseMessage(
                tool_call_id=function_call.id,
                role="tool",
                name=function_call.function.name,
                content=f"ERROR: {e}",
            )

        log.info("function_call_done")
        return ToolResponseMessage(
            tool_call_id=function_call.id,
            role="tool",
            name=function_call.function.name,
            content=results.content,
        )