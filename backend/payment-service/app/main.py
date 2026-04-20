from fastapi import FastAPI
import threading
from .rabbitmq_consumer import start_consumer

app = FastAPI()

def start_background_consumer():
    print("🔥 MANUAL START: launching RabbitMQ consumer thread", flush=True)

    thread = threading.Thread(target=start_consumer)
    thread.daemon = True
    thread.start()

start_background_consumer()

@app.get("/")
def root():
    return {"message": "Payment Service Running"}