import json
import os
import shutil
import time
from typing import List
import httpx
import structlog
import asyncio
import mcp.types as types
from evaluator.tool_manager import Tool, ToolManager

from .docker import Docker
from .agent import Agent
from .config import get_config
from .datatypes import Result, ResultStats, TestParameters, TestToRun
from .mcp_manager import MCPManager
from .provider.openai_client import OpenAIClient
from .provider.openai_types import ChatParameters, Message, TextMessage, ToolDefinition, ToolFunction, ToolRequestMessage, ToolResponseMessage



LOG = structlog.get_logger(__name__)



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
        tools: List[ToolDefinition],
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



def generate_log_html(log: list[Message]) -> str:
    html = "<html><body>"
    for message in log:
        if isinstance(message, TextMessage):
            html += f"<p><strong>{message.role}:</strong> {message.content}</p>"
        elif isinstance(message, ToolRequestMessage):
            for tool in message.tool_calls:
                html += f"<p><strong>Tool Request:</strong> {tool.id} - {tool.function.name} - {tool.function.arguments}</p>"
        else:
            assert isinstance(message, ToolResponseMessage)
            html += f"<p><strong>Tool Response:</strong> {message.name} - {message.content}</p>"

    html += "</body></html>"
    return html


async def run_test(
    output_folder: str,
    test: TestToRun,
) -> Result:
    LOG.info(
        "starting_test",
        provider=test.provider.name,
        model=test.model,
        test_folder=test.test_folder,
    )
    # Create the provider
    make_request = make_provider(
        url=test.provider.base_url,
        token=test.provider.token,
        model=test.model,
    )

    LOG.info(
        "setting_up_environment",
        provider=test.provider.name,
        model=test.model,
    )
    # Set up environment
    os.makedirs(output_folder, exist_ok=True)
    shutil.copytree(
        os.path.join(test.test_folder),
        os.path.join(output_folder),
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("config.json"),
    )

    # Spin up docker container
    with Docker(
        image=test.test_parameters.docker_image,
        name=f"{test.name}_{test.provider.name}_{test.model}",
        project_folder=output_folder,
    ) as environment:
        
        # Create a MCP manager that has bash tool inside the environment
        mcp_manager = MCPManager({})
        await mcp_manager.start()

        async def bash_tool(args: dict[str, str]) -> types.CallToolResult:
            command = args["command"]
            result = await environment(command)
            content: list[types.TextContent | types.ImageContent | types.EmbeddedResource] = [types.TextContent(
                type="text",
                text=result,
            )]
            return types.CallToolResult(
                content=content
            )
        
        tool_manager = ToolManager(mcp_manager, extra_tools=[
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
                bash_tool
            ),
        ])

        # Create the agent
        agent = Agent(make_llm_request=make_request, tool_manager=tool_manager)

        # Run the test
        initial_messages: list[Message] = [
            TextMessage(role="user", content=test.test_parameters.initial_prompt)
        ]

        LOG.info(
            "beginning_agent_run",
            provider=test.provider.name,
            model=test.model,
        )
        start_time = time.time()
        log = await agent.run(initial_messages=initial_messages)
        end_time = time.time()
        LOG.info(
            "agent_run_complete",
            provider=test.provider.name,
            model=test.model,
            duration=end_time - start_time,
        )

        # Generate the thumbnail
        thumbnail_base64 = ""  # generate_thumbnail()
    
    log_html = generate_log_html(log)

    result = Result(
        stats=ResultStats(
            time_seconds=end_time - start_time,
        ),
        thumbnail=thumbnail_base64,
        log=log_html,
    )

    return result


async def __main__():
    config = get_config()
    providers = config.providers
    test_folders = os.listdir(config.test_input_directory)

    tests_to_run: list[TestToRun] = []
    for test_folder in test_folders:
        test_settings_file = os.path.join(
            config.test_input_directory, test_folder, "config.json"
        )
        test_parameters = TestParameters.model_validate(
            json.load(open(test_settings_file, "r"))
        )
        for provider in providers:
            for model in provider.models:
                tests_to_run.append(
                    TestToRun(
                        name=test_folder,
                        test_parameters=test_parameters,
                        provider=provider,
                        model=model,
                        test_folder=os.path.join(config.test_input_directory, test_folder),
                    )
                )
    
    # Sort by provider name and model name
    tests_to_run.sort(
        key=lambda x: (x.provider.name, x.model)
    )

    for test in tests_to_run:
        output_folder = os.path.join(
            os.path.abspath(config.test_output_directory), test.provider.name, test.model
        )
        results = await run_test(output_folder, test)
        # Save the results
        with open(
            os.path.join(output_folder, "log.html"), "w"
        ) as f:
            f.write(results.log)
        
        with open(
            os.path.join(output_folder, "stats.json"), "w"
        ) as f:
            f.write(results.stats.model_dump_json())

        with open(
            os.path.join(output_folder, "thumbnail.png"), "wb"
        ) as f:
            f.write(results.thumbnail)
        


if __name__ == "__main__":
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.PrintLoggerFactory(),
    )
    LOG.info("Starting evaluator")

    asyncio.run(__main__())