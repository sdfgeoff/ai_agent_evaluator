from contextlib import AsyncExitStack
import logging
from mcp import ClientSession, StdioServerParameters, Tool
from mcp.client.stdio import stdio_client
import mcp.types as types


log = logging.getLogger(__name__)


MCP_SERVERS: dict[str, StdioServerParameters] = {
    # "slack": StdioServerParameters(
    #     command="docker",  # Executable
    #     args=[
    #         "run",
    #         "-i",
    #         "--rm",
    #         "-e",
    #         f"SLACK_BOT_TOKEN={config.slack_bot_token}",
    #         "-e",
    #         f"SLACK_TEAM_ID={config.slack_team_id}",
    #         "mcp/slack"
    #     ],
    # ),
    "filesystem": StdioServerParameters(
        # command="docker",  # Executable
        # args=[
        #     "run",
        #     "-i",
        #     "--rm",
        #     "-v",
        #     "/projects:/projects",
        #     "mcp/filesystem",
        #     "/projects",
        # ],
        command="npx",
        args=[
            "-y",
            "@modelcontextprotocol/server-filesystem",
            "./projects",
        ],
    ),
    # "mcp-atlassian": StdioServerParameters(
    #   command="uvx",
    #   args=["mcp-atlassian"],
    #   env={
    #     "CONFLUENCE_URL": "https://carboncrop.atlassian.net/wiki",
    #     "CONFLUENCE_USERNAME": config.atlassian_username,
    #     "CONFLUENCE_API_TOKEN": config.atlassian_token,
    #     "JIRA_URL": "https://carboncrop.atlassian.net/jira",
    #     "JIRA_USERNAME": config.atlassian_username,
    #     "JIRA_API_TOKEN": config.atlassian_token,
    #     "JIRA_PROJECTS_FILTER": "CAR",
    #     "CONFLUENCE_SPACES_FILTER": "CAR",
    #     "READ_ONLY_MODE": "true",
    #   }
    # )
}


class MCPManager:
    def __init__(self, servers: dict[str, StdioServerParameters]):
        self.servers = servers
        self.sessions: dict[str, ClientSession] = {}

        self.exit_stack = AsyncExitStack()

        self.tools: dict[
            str, tuple[str, Tool]
        ] = {}  # Map from a tool name to a tool object and server name

    async def start(self):
        for server_name, params in self.servers.items():
            log.info(f"Connecting to {server_name} server")

            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(params)
            )
            self.stdio, self.write = stdio_transport
            session = await self.exit_stack.enter_async_context(
                ClientSession(self.stdio, self.write)
            )
            self.sessions[server_name] = session
            # Initialize the connection
            await session.initialize()

            # List available tools
            tools = await session.list_tools()

            for tool in tools.tools:
                assert tool.name not in self.tools, f"Duplicate tool name: {tool.name}"
                self.tools[tool.name] = (server_name, tool)
                log.info(f"Found tool: {tool.name} ({server_name})")

    def get_tools(self) -> list[Tool]:
        return [t[1] for t in self.tools.values()]

    async def call_tool(
        self, tool_name: str, arguments: dict[str, str]
    ) -> types.CallToolResult:
        """Call a tool with the given name and arguments"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")

        server_name, tool = self.tools[tool_name]
        session = self.sessions[server_name]

        log.info(f"Calling tool {tool_name} on {server_name} with args {arguments}")

        results = await session.call_tool(tool.name, arguments)

        log.info(f"Tool {tool_name} returned {results}")

        return results
