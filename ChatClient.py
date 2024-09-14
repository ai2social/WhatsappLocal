from pydantic import BaseModel
import httpx

class Request(BaseModel):
    message: str


class Response(BaseModel):
    content: str


class ChatClient:
    def __init__(self, url):
        self.url = url
        self.client = httpx.AsyncClient()

    async def ainvoke(self, request: Request, session_id: str) -> Response:
        response = await self.client.post(
            f"{self.url}/supervisor/{session_id}",
            json={
                "message": request.message
            },
        )
        return Response(content=response.json()['content'])



