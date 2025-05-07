from .provider.openai_types import Message
from .provider.openai_types import TextMessage, ToolRequestMessage, ToolResponseMessage


import mcp.types as types


from xml.sax.saxutils import escape


def generate_log_html(log: list[Message]) -> str:
    html = "<html>" \
    "<style>" \
    "body { font-family: Arial, sans-serif; background: grey; }" \
    ".block { margin: 5px; padding: 5px; white-space: pre-wrap; background: white; }" \
    "</style>" \
    "<body>"
    for message in log:
        if isinstance(message, TextMessage):
            html += f'<div class="block"><strong>{message.role}:</strong> {escape(message.content)}</div>'
        elif isinstance(message, ToolRequestMessage):
            for tool in message.tool_calls:
                html += f'<div class="block"><strong>Tool Request:</strong> {tool.id} - {tool.function.name} - {escape(tool.function.arguments)}</div>'
        else:
            assert isinstance(message, ToolResponseMessage)
            content = ''
            if isinstance(message.content, list):
                for item in message.content:
                    if isinstance(item, types.TextContent):
                        content += f'<p>{escape(item.text)}</p>'
                    elif isinstance(item, types.ImageContent):
                        content += f'<img src="{item.data}" alt="Image" />'
                    elif isinstance(item, types.EmbeddedResource):
                        resource = item.resource
                        if isinstance(resource, types.TextResourceContents):
                            content += f'<p>Embedded Resource: {escape(resource.text)}</p>'
                        elif isinstance(resource, types.BlobResourceContents):
                            content += f'<p>Embedded Resource: {escape(resource.blob)}</p>'
            else:
                content = escape(message.content)
            html += f'<div class="block"><strong>Tool Response:</strong> {message.name} - {content}</div>'

    html += "</body></html>"
    return html