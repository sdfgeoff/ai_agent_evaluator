from agent.agent.provider.openai_types import Message
from agent.agent.provider.openai_types import TextMessage, ToolRequestMessage, ToolResponseMessage
import mcp.types as types


from xml.sax.saxutils import escape

from .html import Tag


def generate_log_html(log: list[Message]) -> str:
    with Tag("html") as html:
        with Tag("style", html) as style:
            style.add(
                """
                body { font-family: Arial, sans-serif; background: grey; }
                .block { margin: 5px; padding: 5px; white-space: pre-wrap; background: white; }
                """
            )

        with Tag("body", html) as body:
            for message in log:
                with Tag("div", body, class_="block") as div:
                    if isinstance(message, TextMessage):
                        with Tag("strong", div) as strong:
                            strong.add(f"{message.role}:")
                        div.add(f" {escape(message.content)}")
                    elif isinstance(message, ToolRequestMessage):
                        for tool in message.tool_calls:
                            with Tag("strong", div) as strong:
                                strong.add(f"Tool Request:")
                            div.add(f" {tool.id} - {tool.function.name} - {escape(tool.function.arguments)}")
                    else:
                        assert isinstance(message, ToolResponseMessage)
                        with Tag("strong", div) as strong:
                            strong.add(f"Tool Response:")
                        
                        if isinstance(message.content, list):
                            for item in message.content:
                                if isinstance(item, types.TextContent):
                                    with Tag("p", div) as p:
                                        p.add(escape(item.text))
                                elif isinstance(item, types.ImageContent):
                                    with Tag("img", div, src=item.data, alt="Image") as img:
                                        pass
                                else:
                                    assert isinstance(item, types.EmbeddedResource)
                                    resource = item.resource
                                    if isinstance(resource, types.TextResourceContents):
                                        with Tag("p", div) as p:
                                            p.add("Embedded Resource: ")
                                            p.add(escape(resource.text))
                                    else:
                                        assert isinstance(resource, types.BlobResourceContents)
                                        with Tag("p", div) as p:
                                            p.add("Embedded Resource: ")
                                            p.add(escape(resource.blob))

                        else:
                            content = escape(message.content)
                            with Tag("p", div) as p:
                                p.add(f"{message.name} - {content}")

    return str(html)