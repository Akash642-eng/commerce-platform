from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from shared.logging.logger import log_event

from .database import Base, engine
from .routes import categories, products

app = FastAPI(title="Product Service")


Instrumentator().instrument(app).expose(app)


Base.metadata.create_all(bind=engine)


app.include_router(products.router)
app.include_router(categories.router)


@app.on_event("startup")
def startup_event():

    log_event(
        service="product-service",
        event="startup",
        trace_id="system",
        message="Product Service started successfully",
    )


@app.get("/")
def read_root():

    return {"service": "Product Service Running"}


@app.get("/health")
def health():

    return {"status": "healthy"}
