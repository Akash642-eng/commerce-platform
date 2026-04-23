from fastapi import FastAPI
from .database import engine, Base
from .routes import orders


import threading
from .payment_consumer import start_payment_consumer

from .payment_failed_consumer import start_failed_consumer

app = FastAPI(title="Order Service")

Base.metadata.create_all(bind=engine)

app.include_router(orders.router)

@app.get("/")
def root():
    return {"service": "Order Service Running"}

def start_consumer():
    thread = threading.Thread(target=start_payment_consumer)
    thread.daemon = True
    thread.start()

start_consumer()


import threading

def start_failed():
    t = threading.Thread(target=start_failed_consumer)
    t.daemon = True
    t.start()

start_failed()