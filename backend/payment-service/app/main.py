from fastapi import FastAPI
import threading

from .rabbitmq_consumer import start_consumer
from .dlq_consumer import start_dlq_consumer

app = FastAPI()


def start_background_consumers():
    print("🔥 Starting all consumers...", flush=True)

    t1 = threading.Thread(target=start_consumer, daemon=True)
    t2 = threading.Thread(target=start_dlq_consumer, daemon=True)

    t1.start()
    t2.start()


start_background_consumers()


@app.get("/")
def root():
    return {"message": "Payment Service Running"}