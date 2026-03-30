from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from ..redis_client import redis_client
import json

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/")
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    new_product = models.Product(
        name=product.name,
        description=product.description,
        price=product.price,
        category_id=product.category_id
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    # Clear cache when new product added
    redis_client.delete("products")

    return new_product


@router.get("/")
def get_products(db: Session = Depends(get_db)):
    # Check Redis cache first
    cached_products = redis_client.get("products")

    if cached_products:
        return json.loads(cached_products)

    # If not in cache, get from DB
    products = db.query(models.Product).all()

    result = []
    for p in products:
        result.append({
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "price": float(p.price),
            "category_id": p.category_id
        })

    # Store in Redis for 60 seconds
    redis_client.set("products", json.dumps(result), ex=60)

    return result