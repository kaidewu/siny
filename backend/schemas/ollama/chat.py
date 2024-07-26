from pydantic import BaseModel
import uuid
from typing import Optional, Any
from settings.settings import settings


class ChatInsertModel(BaseModel):
    id: str
    model: str
    created_at: str
    message: dict


class ChatMessagesModel(BaseModel):
    role: str = "user"
    content: str
    images: Optional[str] = None


class ChatModel(BaseModel):
    id: uuid.UUID
    model: str = settings.OLLAMA_MODEL
    message: ChatMessagesModel
    format: Optional[str] = None
    options: Optional[Any] = None
    stream: Optional[bool] = False
    keep_alive: Optional[str] = None


class AskChatModel(BaseModel):
    filePath: str
    errorMessage: str
    dataUsed: str
