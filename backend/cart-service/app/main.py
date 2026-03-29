from fastapi import FastAPI
from .database import engine, Base
from .routes import cart

app = FastAPI(title="Cart Service")

Base.metadata.create_all(bind=engine)

app.include_router(cart.router)

@app.get("/")
def root():
    return {"service": "Cart Service Running"}