from fastapi import FastAPI

from prometheus_fastapi_instrumentator import Instrumentator

from .database import engine, Base
from .routes import cart

app = FastAPI(title="Cart Service")

Instrumentator().instrument(app).expose(app)

Base.metadata.create_all(bind=engine)

app.include_router(cart.router)

@app.get("/")
def root():
    return {"service": "Cart Service Running"}