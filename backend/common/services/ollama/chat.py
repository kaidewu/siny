import httpx
from backend import __version__
import platform
from settings.settings import settings
from schemas.ollama.chat import ChatModel


class Chat:
    def __init__(
            self,
            chat: ChatModel
    ) -> None:
        self.ollama_api: str = f"{settings.OLLAMA_API}/api/chat"
        self.chat: ChatModel = chat
        self.headers: dict = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': f'sinasuite-dl/{__version__} ({platform.machine()} {platform.system().lower()}) Python/{platform.python_version()}'
        }

    def response(self) -> str:
        with httpx.Client() as client:
            response = client.post(
                url=self.ollama_api,
                headers=self.headers,
                json={
                    "model": self.chat.model,
                    "messages": [{
                        "role": self.chat.messages.role,
                        "content": self.chat.messages.content,
                        "images": self.chat.messages.images if self.chat.messages.images else None
                    }],
                    "format": self.chat.format if self.chat.format else None,
                    "options": self.chat.options if self.chat.options else None,
                    "stream": self.chat.stream if self.chat.stream else False,
                    "keep_alive": self.chat.keep_alive if self.chat.keep_alive else None
                },
                timeout=2000
            )

        return response.json()["message"].get("content")
