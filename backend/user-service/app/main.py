from fastapi import FastAPI

from prometheus_fastapi_instrumentator import Instrumentator

from .database import engine, Base

from .routes import users
from .routes import auth


app = FastAPI(
    title="User Service"
)


Instrumentator().instrument(app).expose(app)


Base.metadata.create_all(bind=engine)


app.include_router(users.router)
app.include_router(auth.router)


@app.get("/")
def root():

    return {
        "service": "User Service Running"
    }


@app.get("/health")
def health_check():

    return {
        "status": "healthy"
    }


@app.get("/ready")
def readiness_check():

    return {
        "status": "ready"
    }