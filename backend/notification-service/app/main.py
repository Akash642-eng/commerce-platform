from fastapi import FastAPI
from .database import engine, Base
from .routes import notifications

app = FastAPI(title="Notification Service")

Base.metadata.create_all(bind=engine)

app.include_router(notifications.router)

@app.get("/")
def root():
    return {"service": "Notification Service Running"}