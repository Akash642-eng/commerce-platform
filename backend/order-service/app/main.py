from fastapi import FastAPI
from .database import engine, Base
from .routes import orders

app = FastAPI(title="Order Service")

Base.metadata.create_all(bind=engine)

app.include_router(orders.router)

@app.get("/")
def root():
    return {"service": "Order Service Running"}