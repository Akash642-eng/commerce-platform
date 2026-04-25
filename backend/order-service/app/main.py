from fastapi import FastAPI
from .database import engine, Base
from .routes import orders

import threading

from .payment_consumer import start_payment_consumer
from .payment_failed_consumer import start_failed_consumer
from .inventory_consumer import start_inventory_consumer


app = FastAPI(title="Order Service")

Base.metadata.create_all(bind=engine)

app.include_router(orders.router)


@app.get("/")
def root():
    return {"service": "Order Service Running"}

def start_all_consumers():
    print("🚀 Starting all order-service consumers...", flush=True)

    threading.Thread(target=start_payment_consumer, daemon=True).start()
    threading.Thread(target=start_failed_consumer, daemon=True).start()
    threading.Thread(target=start_inventory_consumer, daemon=True).start()

@app.on_event("startup")
def startup_event():
    start_all_consumers()