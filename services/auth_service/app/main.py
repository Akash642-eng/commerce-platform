from fastapi import FastAPI

from prometheus_fastapi_instrumentator import Instrumentator

from .routers import auth

from shared.logging.logger import log_event


app = FastAPI(
    title="Auth Service"
)


Instrumentator().instrument(app).expose(app)


app.include_router(auth.router)


@app.on_event("startup")
def startup_event():

    log_event(
        service="auth-service",
        event="startup",
        trace_id="system",
        message="Auth Service started"
    )


@app.get("/")
def root():

    return {
        "message": "Auth Service Running"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }