from fastapi import FastAPI

from prometheus_fastapi_instrumentator import Instrumentator

from .database import engine
from .database import Base

from .routes import orders

import threading

from .payment_consumer import start_payment_consumer
from .payment_failed_consumer import start_failed_consumer
from .inventory_consumer import start_inventory_consumer

from .logger import log_event


app = FastAPI(
    title="Order Service",
    redirect_slashes=False
)


Instrumentator().instrument(app).expose(app)


Base.metadata.create_all(bind=engine)


app.include_router(orders.router)


@app.get("/")
def root():

    return {
        "service": "Order Service Running"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


def start_all_consumers():

    log_event(
        service="order-service",
        event="startup",
        trace_id="system",
        message="Starting all order-service consumers..."
    )

    threading.Thread(
        target=start_payment_consumer,
        daemon=True
    ).start()

    threading.Thread(
        target=start_failed_consumer,
        daemon=True
    ).start()

    threading.Thread(
        target=start_inventory_consumer,
        daemon=True
    ).start()


@app.on_event("startup")
def startup_event():

    start_all_consumers()