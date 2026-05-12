from fastapi import FastAPI

from prometheus_fastapi_instrumentator import Instrumentator

from .database import engine
from .database import Base

from .routes import notifications

from .consumer import start_consumer

import threading


app = FastAPI(
    title="Notification Service"
)


Instrumentator().instrument(app).expose(app)


Base.metadata.create_all(bind=engine)


app.include_router(notifications.router)


@app.on_event("startup")
def startup_event():

    thread = threading.Thread(
        target=start_consumer,
        daemon=True
    )

    thread.start()


@app.get("/")
def root():

    return {
        "service": "Notification Service Running"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }