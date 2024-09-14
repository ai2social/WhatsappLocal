from pydantic import BaseModel
import httpx
import logging

class Request(BaseModel):
    message: str


class Response(BaseModel):
    content: str


class ChatClient:
    def __init__(self, url):
        self.url = url
    async def ainvoke(self, request: Request, session_id: str) -> Response:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.url}/supervisor/{session_id}",
                json={
                    "message": request.message
                },
            )
            logging.info(response)
            return Response(content=response.json()['content'])



