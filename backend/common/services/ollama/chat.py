import httpx
import __version__
import platform
from datetime import datetime
from settings.settings import settings
from schemas.ollama.chat import ChatModel, ChatMessagesModel, ChatInsertModel
from typing import Any


class Chat:
    def __init__(
            self,
            chat: ChatModel,
            uuid: str,
            mongodb: Any
    ) -> None:
        self.chatbot_db: Any = mongodb
        self.ollama_api: str = f"{settings.OLLAMA_API}/api/chat"
        self.chat: ChatModel = chat
        self.headers: dict = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': f'sinasuite-dl/{__version__} ({platform.machine()} {platform.system().lower()}) Python/{platform.python_version()}'
        }

        self.uuid: str = uuid

    def __save_message(
            self,
            message: ChatInsertModel
    ) -> None:
        collection = self.chatbot_db.get_collection()

        collection.insert_one({
            "id": message.id,
            "model": message.model,
            "createdAt": message.created_at,
            "message": message.message
        })

    def __get_messages(self) -> list[ChatMessagesModel]:
        collection = self.chatbot_db.get_collection()

        list_chat_messages: list[ChatMessagesModel] = []

        for message in collection.find({"id": self.uuid}):
            list_chat_messages.append(
                ChatMessagesModel(
                    **
                    {
                        "role": message["message"].get("role"),
                        "content": message["message"].get("content"),
                        "images": message["message"].get("images")
                    }
                )
            )

        return list_chat_messages

    def _json_message(self) -> list[dict]:

        self.__save_message(message=ChatInsertModel(
            id=self.uuid,
            model=self.chat.model,
            created_at=datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            message={
                "role": self.chat.message.role,
                "content": self.chat.message.content,
                "images": self.chat.message.images
            }
        ))

        list_messages: list[dict] = []

        for message in self.__get_messages():
            list_messages.append({
                "role": message.role,
                "content": message.content,
                "images": message.images
            })

        return list_messages

    def response(self) -> str:
        with httpx.Client() as client:
            response = client.post(
                url=self.ollama_api,
                headers=self.headers,
                json={
                    "model": self.chat.model,
                    "messages": self._json_message(),
                    "format": self.chat.format if self.chat.format else None,
                    "options": self.chat.options if self.chat.options else None,
                    "stream": self.chat.stream if self.chat.stream else False,
                    "keep_alive": self.chat.keep_alive if self.chat.keep_alive else None
                },
                timeout=2000
            )

        response_json = response.json()

        if response.status_code == 200:
            self.__save_message(message=ChatInsertModel(
                id=self.uuid,
                model=response_json.get("model"),
                created_at=response_json.get("created_at"),
                message={
                    "role": response_json["message"].get("role"),
                    "content": response_json["message"].get("content"),
                    "images": response_json["message"].get("images") if response_json["message"].get("images") else None
                }
            ))
        else:
            raise Exception(response_json.get("error"))

        return response_json["message"].get("content")
