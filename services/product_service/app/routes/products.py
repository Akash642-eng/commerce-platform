from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from sqlalchemy.orm import Session

from ..database import get_db

from .. import models
from .. import schemas

from ..redis_client import redis_client

import json


router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


@router.post(
    "/",
    response_model=schemas.ProductResponse
)
def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db)
):

    category = db.query(
        models.Category
    ).filter(
        models.Category.id == product.category_id
    ).first()

    if not category:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    new_product = models.Product(
        name=product.name,
        description=product.description,
        price=product.price,
        stock=product.stock,
        category_id=product.category_id
    )

    db.add(new_product)

    db.commit()

    db.refresh(new_product)

    redis_client.delete("products")

    return new_product


@router.get(
    "/",
    response_model=list[schemas.ProductResponse]
)
def get_products(
    db: Session = Depends(get_db)
):

    cached_products = redis_client.get("products")

    if cached_products:

        return json.loads(cached_products)

    products = db.query(
        models.Product
    ).all()

    result = []

    for p in products:

        result.append({
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "price": float(p.price),
            "stock": p.stock,
            "is_active": p.is_active,
            "category_id": p.category_id
        })

    redis_client.set(
        "products",
        json.dumps(result),
        ex=60
    )

    return result


@router.get(
    "/{product_id}",
    response_model=schemas.ProductResponse
)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):

    product = db.query(
        models.Product
    ).filter(
        models.Product.id == product_id
    ).first()

    if not product:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return product


@router.put(
    "/{product_id}",
    response_model=schemas.ProductResponse
)
def update_product(
    product_id: int,
    updated_product: schemas.ProductUpdate,
    db: Session = Depends(get_db)
):

    product_query = db.query(
        models.Product
    ).filter(
        models.Product.id == product_id
    )

    product = product_query.first()

    if not product:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    product_query.update(
        updated_product.dict(),
        synchronize_session=False
    )

    db.commit()

    redis_client.delete("products")

    return product_query.first()


@router.delete(
    "/{product_id}"
)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
):

    product_query = db.query(
        models.Product
    ).filter(
        models.Product.id == product_id
    )

    product = product_query.first()

    if not product:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    product_query.delete(
        synchronize_session=False
    )

    db.commit()

    redis_client.delete("products")

    return {
        "message": "Product deleted successfully"
    }