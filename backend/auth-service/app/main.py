from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from .routers import auth

app = FastAPI(title="Auth Service")

Instrumentator().instrument(app).expose(app)

app.include_router(auth.router)


@app.get("/")
def root():
    return {"message": "Auth Service Running"}