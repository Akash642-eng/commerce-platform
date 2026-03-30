from fastapi import FastAPI
import threading
import time
from .rabbitmq_consumer import start_consumer

app = FastAPI()

def consumer_worker():
    while True:
        try:
            print("Starting RabbitMQ consumer...")
            start_consumer()
        except Exception as e:
            print("RabbitMQ connection failed. Retrying in 5 seconds...")
            print(e)
            time.sleep(5)

@app.on_event("startup")
def startup_event():
    print("APP STARTUP - Starting RabbitMQ thread")
    thread = threading.Thread(target=consumer_worker)
    thread.daemon = True
    thread.start()

@app.get("/")
def root():
    return {"message": "Payment Service Running"}