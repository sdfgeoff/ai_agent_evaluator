import asyncio
import json
import os
import time
import traceback
import httpx
from pydantic import BaseModel
import structlog

from .log_to_html import generate_log_html

from .datatypes import Result, ResultStats, TestToRun
from .provider.openai_client import OpenAIClient
from .provider.openai_types import (
    ChatParameters,
    ToolDefinition,
    ToolFunction,
)
from .provider.openai_types import Message, TextMessage
from .agent import Agent
from .mcp_manager import MCPManager
import mcp.types as types
from .tool_manager import Tool, ToolManager


def make_provider(url: str, token: str, model: str):
    llm_client = httpx.AsyncClient(
        base_url=url,
        timeout=60 * 5,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )

    provider = OpenAIClient(
        connection=llm_client,
    )

    async def make_request(
        messages: list[Message],
        tools: list[ToolDefinition],
    ) -> Message:
        res = await provider.v1_chat_completions(
            llm_request=ChatParameters(
                model=model,
                messages=messages,
                tools=tools,
                stream=False,
            )
        )
        assert len(res.choices) == 1, "Expected exactly one choice"
        return res.choices[0].message

    return make_request


LOG = structlog.get_logger(__name__)


async def main(test: TestToRun):
    # Create the provider
    os.chdir(test.test_folder)

    make_request = make_provider(
        url=test.provider.base_url,
        token=test.provider.token,
        model=test.model,
    )

    # Create a MCP manager that has bash tool inside the environment
    mcp_manager = MCPManager({})
    await mcp_manager.start()

    async def bash_tool(args: dict[str, str]) -> types.CallToolResult:
        command = args["command"]
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, os.system, command)
        content: list[
            types.TextContent | types.ImageContent | types.EmbeddedResource
        ] = [
            types.TextContent(
                type="text",
                text=json.dumps({
                    "output": str(result),
                    "status": result,
                }),
            )
        ]
        return types.CallToolResult(content=content)

    tool_manager = ToolManager(
        mcp_manager,
        extra_tools=[
            Tool(
                ToolDefinition(
                    type="function",
                    function=ToolFunction(
                        name="bash",
                        description="Run a bash command",
                        parameters={
                            "type": "object",
                            "properties": {
                                "command": {
                                    "type": "string",
                                    "description": "The command to run",
                                },
                            },
                            "required": ["command"],
                        },
                    ),
                ),
                bash_tool,
            ),
        ],
    )

    # Create the agent
    agent = Agent(make_llm_request=make_request, tool_manager=tool_manager)

    # Run the test
    initial_messages: list[Message] = [
        TextMessage(role="user", content=test.test_parameters.initial_prompt),
    ]

    LOG.info(
        "beginning_agent_run",
        provider=test.provider.name,
        model=test.model,
    )
    start_time = time.time()
    try:
        await agent.run(initial_messages=initial_messages)
        log = agent.messages
    except Exception as e:
        log = agent.messages
        LOG.exception(
            "agent_run_failed",
            provider=test.provider.name,
            model=test.model,
        )
        log.append(TextMessage(role="assistant", content=traceback.format_exc()))

    end_time = time.time()
    LOG.info(
        "agent_run_ended",
        provider=test.provider.name,
        model=test.model,
        duration=end_time - start_time,
    )

    # Generate the thumbnail
    thumbnail_base64 = b""  # generate_thumbnail()

    log_html = generate_log_html(log)

    results = Result(
        stats=ResultStats(
            time_seconds=end_time - start_time,
        ),
        thumbnail=thumbnail_base64,
        log=log_html,
    )

    # Save the results
    with open(os.path.join(test.test_folder, "log.html"), "w") as f:
        f.write(results.log)

    with open(os.path.join(test.test_folder, "stats.json"), "w") as f:
        f.write(results.stats.model_dump_json())

    with open(os.path.join(test.test_folder, "thumbnail.png"), "wb") as f:
        f.write(results.thumbnail)


if __name__ == "__main__":
    test_json = os.environ.get("TEST_CONFIG")
    if test_json is None:
        raise RuntimeError("TEST_CONFIG environment variable not set")

    test_conf = TestToRun.model_validate_json(test_json)

    asyncio.run(main(test_conf))
