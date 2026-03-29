from fastapi import FastAPI
from .database import engine, Base
from .routes import delivery

app = FastAPI(title="Delivery Service")

Base.metadata.create_all(bind=engine)

app.include_router(delivery.router)

@app.get("/")
def root():
    return {"service": "Delivery Service Running"}