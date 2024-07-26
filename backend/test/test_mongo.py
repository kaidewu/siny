import httpx
from backend.settings.settings import settings


# Test connection to mongodb service
def test_connection_mongo() -> None:
    with httpx.Client() as client:
        response = client.get(
            url=settings.MONGO_ENDPOINT
        )

    assert response.status_code == 200
