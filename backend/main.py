import uvicorn
import fire
from settings.settings import settings


def main() -> None:
    print(f"Listening on {settings.HOST}:{settings.SERVICE_PORT}")
    uvicorn.run(
        app="app:app",
        host=settings.HOST,
        port=settings.SERVICE_PORT,
        use_colors=True
    )


if __name__ == "__main__":
    fire.Fire(main)
