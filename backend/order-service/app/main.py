from fastapi import FastAPI
from .database import engine, Base
from .routes import orders


import threading
from .payment_consumer import start_payment_consumer

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