import httpx
from backend.settings.settings import settings


# Test of connection to ollama REST API
def test_connection_ollama() -> None:
    with httpx.Client() as client:
        response = client.get(
            url=settings.OLLAMA_API
        )

    assert response.status_code == 200


# Test if the model llama3 is running
def test_client_chat() -> None:
    with httpx.Client() as client:
        response = client.post(
            url=f"{settings.OLLAMA_API}/api/chat",
            json={
                'model': settings.OLLAMA_MODEL,
                'messages': [{'role': 'user', 'content': 'Give me a random number between 1 and 3'}],
                'tools': [],
                'stream': False,
                'format': '',
                'options': {},
                'keep_alive': None,
            }
        )

    assert response.status_code == 200
    assert response.json()["model"] == settings.OLLAMA_MODEL
    assert response.json()["message"]["role"] == "assistant"
    assert response.json()["message"]["content"] != ""
