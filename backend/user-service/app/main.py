from fastapi import FastAPI
from .database import engine, Base
from .routes import users

app = FastAPI(title="User Service")

Base.metadata.create_all(bind=engine)

app.include_router(users.router)

@app.get("/")
def root():
    return {"service": "User Service Running"}