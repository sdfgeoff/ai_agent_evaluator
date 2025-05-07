import httpx
from .openai_types import ChatParameters, ChatResponse

class OpenAIClient:
    def __init__(self, connection: httpx.AsyncClient):
        self.connection = connection

    async def v1_chat_completions(
        self,
        llm_request: ChatParameters,
    ):
        resp = await self.connection.post(
            "/v1/chat/completions",
            json=llm_request.model_dump(mode="json"),
        )
        assert resp.status_code == 200, resp.text
        resp.raise_for_status()

        return ChatResponse.model_validate(resp.json())
