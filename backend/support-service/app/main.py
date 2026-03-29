from fastapi import FastAPI
from .database import engine, Base
from .routes import support

app = FastAPI(title="Support Service")

Base.metadata.create_all(bind=engine)

app.include_router(support.router)

@app.get("/")
def root():
    return {"service": "Support Service Running"}