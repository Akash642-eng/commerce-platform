from fastapi import FastAPI

from prometheus_fastapi_instrumentator import Instrumentator

from .database import engine, Base
from .routes import delivery

app = FastAPI(
    title="Delivery Service"
)

Instrumentator().instrument(app).expose(app)

Base.metadata.create_all(bind=engine)

app.include_router(delivery.router)


@app.get("/")
def root():
    return {
        "service": "Delivery Service Running"
    }