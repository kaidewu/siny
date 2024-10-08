import sys
from pathlib import Path
from common.errors import raise_http_error
from settings.settings import settings
from common.services.ollama.chat import Chat
from schemas.ollama.chat import ChatModel, AskChatModel
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.post(
    path="/ollama/chat",
    tags=["OLLAMA CHAT AI"],
    summary="OLLAMA AI MODEL"
)
async def api_ollama_chat(
        chat_data: ChatModel
) -> JSONResponse:

    try:
        chat: Chat = Chat(
            chat=chat_data
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
                    "content": f"You are a Backend Software Developer with 25+ years of experience in all "
                               f"language of programming that you learned in the Harvard University "
                               f"in the computer sciences degree, working in Google, Amazon, Apple, Microsoft, "
                               f"Spotify, CrownStrike, Nvidia, Facebook (Meta Platforms), American Express, "
                               f"Pfizer, Starbucks Corp, Paypal, SpaceX and NASA.\n"
                               f"In this Project called `sinasuite-dl`, where my github "
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
