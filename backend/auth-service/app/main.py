from fastapi import FastAPI
from app.routers import auth
from app.database import engine, Base
from app.models import user

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Auth Service")

app.include_router(auth.router, prefix="/auth", tags=["Auth"])

@app.get("/")
def health_check():
    return {"status": "Auth Service Running"}