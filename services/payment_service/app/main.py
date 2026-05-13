from fastapi import FastAPI

from prometheus_fastapi_instrumentator import Instrumentator

import threading

from .rabbitmq_consumer import start_consumer
from .dlq_consumer import start_dlq_consumer

from shared.logging.logger import log_event


app = FastAPI(
    title="Payment Service"
)


Instrumentator().instrument(app).expose(app)


def start_background_consumers():

    log_event(
        service="payment-service",
        event="startup",
        trace_id="system",
        message="Starting all consumers..."
    )

    t1 = threading.Thread(
        target=start_consumer,
        daemon=True
    )

    t2 = threading.Thread(
        target=start_dlq_consumer,
        daemon=True
    )

    t1.start()
    t2.start()


@app.on_event("startup")
def startup_event():

    start_background_consumers()


@app.get("/")
def root():

    log_event(
        service="payment-service",
        event="root_access",
        trace_id="system",
        message="Root endpoint accessed"
    )

    return {
        "message": "Payment Service Running"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }