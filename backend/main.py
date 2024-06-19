import uvicorn
from settings.settings import settings

if __name__ == "__main__":
    uvicorn.run(app="app:app", host=settings.HOST, port=settings.SERVICE_PORT, reload=True)
