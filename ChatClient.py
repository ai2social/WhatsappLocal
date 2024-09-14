import requests
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

    def invoke(self, request: Request, session_id: str) -> Response:
        try:
            response = requests.post(
                f"{self.url}/supervisor/{session_id}",
                json={"message": request.message}
            )
            logging.info(response)
            return Response(content=response.json().get('content'))
        except requests.RequestException as e:
            logging.error(f"Request failed: {e}")
            return Response(content="An error occurred", status_code=500)



