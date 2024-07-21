from pydantic import BaseModel
from typing import Optional, Any
from settings.settings import settings


class ChatMessagesModel(BaseModel):
    role: str = "user"
    content: str
    images: Optional[str] = None


class ChatModel(BaseModel):
    model: str = settings.OLLAMA_MODEL
    messages: ChatMessagesModel
    format: Optional[str] = None
    options: Optional[Any] = None
    stream: Optional[bool] = False
    keep_alive: Optional[str] = None


class AskChatModel(BaseModel):
    filePath: str
    errorMessage: str
    dataUsed: str
