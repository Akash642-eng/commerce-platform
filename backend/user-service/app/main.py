from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from .database import engine, Base
from .routes import users

from shared.tracing import setup_tracing

app = FastAPI(title="User Service")

setup_tracing(app, "user-service")

Instrumentator().instrument(app).expose(app)

Base.metadata.create_all(bind=engine)

app.include_router(users.router)

@app.get("/")
def root():
    return {"service": "User Service Running"}