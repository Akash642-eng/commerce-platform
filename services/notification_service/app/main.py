import threading

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from shared.logging.logger import log_event

from .consumer import start_consumer
from .database import Base, engine
from .routes import notifications

from shared.tracing.tracing import setup_tracing

app = FastAPI(title="Notification Service")
setup_tracing(app, "notification-service")

Instrumentator().instrument(app).expose(app)


Base.metadata.create_all(bind=engine)


app.include_router(notifications.router)


@app.on_event("startup")
def startup_event():

    log_event(
        service="notification-service",
        event="startup",
        trace_id="system",
        message="Notification Service started successfully",
    )

    thread = threading.Thread(target=start_consumer, daemon=True)

    thread.start()


@app.get("/")
def root():

    return {"service": "Notification Service Running"}


@app.get("/health")
def health():

    return {"status": "healthy"}
