import sys
from pathlib import Path
from common.errors import raise_http_error
from settings.settings import settings
from common.services.ollama.chat import Chat
from schemas.ollama.chat import ChatModel, AskChatModel
from common.database.mongodb.pool import get_db_pool
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.post(
    path="/ollama/chat/{uuid}",
    tags=["OLLAMA CHAT AI"],
    summary="OLLAMA AI MODEL"
)
async def api_ollama_chat(
        uuid: str,
        chat_data: ChatModel
) -> JSONResponse:

    try:
        get_db = get_db_pool()

        chat: Chat = Chat(
            chat=chat_data,
            uuid=uuid,
            mongodb=get_db
        )

        return JSONResponse(
            content={
                "message": chat.response()
            }
        )
    except:
        raise_http_error(file=__file__, sys_traceback=sys.exc_info())


@router.post(
    path="/ollama/internal/chat/",
    tags=["ASK AI INTERNAL"],
    summary="Asking AI if something has error"
)
async def api_internal_chat(
        chat_ask_model: AskChatModel
) -> JSONResponse:
    try:
        chat_model: ChatModel = ChatModel(
            **
            {
                "messages": {
                    "content": f"In this Project called `sinasuite-dl`, where my github "
                               f"link is: https://github.com/kaidewu/sinasuite-dl, it's made in Python using "
                               f"this packages: `{Path(settings.REQUIREMENTS_TXT).read_text()}`.\n"
                               f"I got this error in Python:\n"
                               f"`{chat_ask_model.errorMessage}`\n"
                               f"I give you my Python code where has happened the error before:\n"
                               f"`{Path(chat_ask_model.filePath).read_text().replace('\"', '\'')}`\n"
                               f"The datas I using are:\n"
                               f"`{chat_ask_model.dataUsed}`"
                },
                "options": {
                    "seed": 101,
                    "temperature": 0.3
                }
            }
        )

        chat: Chat = Chat(
            chat=chat_model
        )

        return JSONResponse(
            content={
                "message": chat.response()
            }
        )
    except:
        raise_http_error(file=__file__, sys_traceback=sys.exc_info())
