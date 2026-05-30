from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from shared.logging.logger import log_event

from .routers import auth

from shared.tracing.tracing import setup_tracing

app = FastAPI(title="Auth Service")
setup_tracing(app, "auth-service")

Instrumentator().instrument(app).expose(app)


app.include_router(auth.router)


@app.on_event("startup")
def startup_event():

    log_event(
        service="auth-service",
        event="startup",
        trace_id="system",
        message="Auth Service started",
    )


@app.get("/")
def root():

    return {"message": "Auth Service Running"}


@app.get("/health")
def health():

    return {"status": "healthy"}
