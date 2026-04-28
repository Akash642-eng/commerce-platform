from fastapi import FastAPI
from .routers import auth

app = FastAPI(title="Auth Service")

app.include_router(auth.router)


@app.get("/")
def root():
    return {"message": "Auth Service Running"}