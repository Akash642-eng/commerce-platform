from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from shared.logging.logger import log_event

from .database import Base, engine
from .routes import delivery

from shared.tracing.tracing import setup_tracing

app = FastAPI(title="Delivery Service")
setup_tracing(app, "delivery-service")


Instrumentator().instrument(app).expose(app)


Base.metadata.create_all(bind=engine)


app.include_router(delivery.router)


@app.on_event("startup")
def startup_event():

    log_event(
        service="delivery-service",
        event="startup",
        trace_id="system",
        message="Delivery Service started successfully",
    )


@app.get("/")
def root():

    return {"service": "Delivery Service Running"}


@app.get("/health")
def health():

    return {"status": "healthy"}
