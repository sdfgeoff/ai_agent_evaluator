import asyncio
import json
import mcp.types as types
from pydantic import BaseModel

from .provider.openai_types import ToolDefinition, ToolFunction
from .tool_manager import Tool


class BashToolArgs(BaseModel):
    command: str


async def bash_tool(args: dict[str, str]) -> types.CallToolResult:
    async with asyncio.timeout(60):
        args_parsed = BashToolArgs.model_validate(args)

        process = await asyncio.create_subprocess_shell(
            args_parsed.command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        status = process.returncode
        content: list[types.TextContent | types.ImageContent | types.EmbeddedResource] = [
            types.TextContent(
                type="text",
                text=json.dumps(
                    {
                        "output": stdout.decode().strip(),
                        "error": stderr.decode().strip(),
                        "status": status,
                    }
                ),
            )
        ]
        return types.CallToolResult(content=content)


BASH_TOOL = Tool(
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
)


class CreateFileToolArgs(BaseModel):
    filename: str
    content: str | None = None


async def create_file_tool(args: dict[str, str]) -> types.CallToolResult:
    args_parsed = CreateFileToolArgs.model_validate(args)
    filename = args_parsed.filename
    content = args_parsed.content or ""
    try:
        with open(filename, "w") as f:
            f.write(content)
    except Exception as e:
        return types.CallToolResult(
            content=[
                types.TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "error": str(e),
                        }
                    ),
                )
            ]
        )
    return types.CallToolResult(
        content=[
            types.TextContent(
                type="text",
                text=json.dumps(
                    {
                        "message": f"File {filename} created successfully",
                    }
                ),
            )
        ]
    )


CREATE_FILE_TOOL = Tool(
    ToolDefinition(
        type="function",
        function=ToolFunction(
            name="create_file",
            description="Create a file with the given content",
            parameters={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "The name of the file to create",
                    },
                    "content": {
                        "type": "string",
                        "description": "The content to write to the file",
                    },
                },
                "required": ["filename"],
            },
        ),
    ),
    create_file_tool,
)
