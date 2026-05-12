from fastapi import FastAPI

from prometheus_fastapi_instrumentator import Instrumentator

from .database import engine
from .database import Base

from .routes import inventory

import threading

from .rabbitmq_consumer import start_consumer
from .release_consumer import start_release_consumer


app = FastAPI(
    title="Inventory Service"
)


Instrumentator().instrument(app).expose(app)


Base.metadata.create_all(bind=engine)


app.include_router(inventory.router)


@app.get("/")
def root():

    return {
        "service": "Inventory Service Running"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


def start_inventory():

    thread = threading.Thread(
        target=start_consumer
    )

    thread.daemon = True

    thread.start()


start_inventory()


def start_release():

    thread = threading.Thread(
        target=start_release_consumer
    )

    thread.daemon = True

    thread.start()


start_release()