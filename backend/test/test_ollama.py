from dotenv import load_dotenv
import httpx
import os

load_dotenv("../.env")


# Test of connection to ollama REST API
def test_connection_ollama():
    with httpx.Client() as client:
        response = client.get(
            url=os.getenv("OLLAMA_API")
        )

    assert response.status_code == 200


# Test if the model llama3 is running
def test_client_chat():
    with httpx.Client() as client:
        response = client.post(
            url=f"{os.getenv("OLLAMA_API")}/api/chat",
            json={
                'model': 'llama3',
                'messages': [{'role': 'user', 'content': 'Give me a random number between 1 and 3'}],
                'tools': [],
                'stream': False,
                'format': '',
                'options': {},
                'keep_alive': None,
            }
        )

    assert response.status_code == 200
    assert response.json()["model"] == "llama3"
    assert response.json()["message"]["role"] == "assistant"
