from fastapi import FastAPI
from .database import engine, Base
from .routes import payments

app = FastAPI(title="Payment Service")

Base.metadata.create_all(bind=engine)

app.include_router(payments.router)

@app.get("/")
def root():
    return {"service": "Payment Service Running"}