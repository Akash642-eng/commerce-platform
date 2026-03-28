from fastapi import FastAPI
from .database import engine, Base
from .routes import products, categories

app = FastAPI(title="Product Service")

Base.metadata.create_all(bind=engine)

app.include_router(products.router)
app.include_router(categories.router)

@app.get("/")
def read_root():
    return {"service": "Product Service Running"}