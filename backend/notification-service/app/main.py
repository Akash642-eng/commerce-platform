from fastapi import FastAPI

from prometheus_fastapi_instrumentator import Instrumentator

from .database import engine, Base
from .routes import notifications

app = FastAPI(title="Notification Service")

Instrumentator().instrument(app).expose(app)

Base.metadata.create_all(bind=engine)

app.include_router(notifications.router)

@app.get("/")
def root():
    return {"service": "Notification Service Running"}