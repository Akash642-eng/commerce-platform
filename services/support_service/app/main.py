from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from shared.logging.logger import log_event

from .database import Base, engine
from .routes import support

from shared.tracing.tracing import setup_tracing

app = FastAPI(title="Support Service")
setup_tracing(app, "support-service")

Instrumentator().instrument(app).expose(app)


Base.metadata.create_all(bind=engine)


app.include_router(support.router)


@app.on_event("startup")
def startup_event():

    log_event(
        service="support-service",
        event="startup",
        trace_id="system",
        message="Support Service started successfully",
    )


@app.get("/")
def root():

    return {"service": "Support Service Running"}


@app.get("/health")
def health():

    return {"status": "healthy"}
