import uvicorn
from settings.settings import settings

if __name__ == "__main__":
    uvicorn.run(app="app:app", host="0.0.0.0", port=settings.SERVICE_PORT, reload=True)
