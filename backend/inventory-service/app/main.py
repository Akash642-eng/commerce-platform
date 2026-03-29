from fastapi import FastAPI
from .database import engine, Base
from .routes import inventory

app = FastAPI(title="Inventory Service")

Base.metadata.create_all(bind=engine)

app.include_router(inventory.router)

@app.get("/")
def root():
    return {"service": "Inventory Service Running"}