from fastapi import FastAPI

from prometheus_fastapi_instrumentator import Instrumentator

from .database import engine
from .database import Base

from .routes import support


app = FastAPI(
    title="Support Service"
)


Instrumentator().instrument(app).expose(app)


Base.metadata.create_all(bind=engine)


app.include_router(support.router)


@app.get("/")
def root():

    return {
        "service": "Support Service Running"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }