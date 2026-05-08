from fastapi import FastAPI

from prometheus_fastapi_instrumentator import Instrumentator

from app.database import engine
from app.database import Base

from app.routes import users

from app import models

from shared.tracing import setup_tracing


models.Base.metadata.create_all(
    bind=engine
)

app = FastAPI(
    title="User Service"
)

setup_tracing(
    app,
    "user-service"
)

Instrumentator().instrument(
    app
).expose(app)

app.include_router(
    users.router
)


@app.get("/")
def root():

    return {
        "service": "User Service Running"
    }