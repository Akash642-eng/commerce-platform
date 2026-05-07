from fastapi import FastAPI
import threading

from .rabbitmq_consumer import start_consumer
from .dlq_consumer import start_dlq_consumer

from .logger import log_event       

app = FastAPI()


def start_background_consumers():
    log_event("payment-service", "SYSTEM", "Starting all consumers...", {})

    t1 = threading.Thread(target=start_consumer, daemon=True)
    t2 = threading.Thread(target=start_dlq_consumer, daemon=True)

    t1.start()
    t2.start()

@app.on_event("startup")
def startup_event():
    start_background_consumers()

@app.get("/")
def root():
    log_event("payment-service", "SYSTEM", "Root endpoint accessed", {})
    return {"message": "Payment Service Running"}