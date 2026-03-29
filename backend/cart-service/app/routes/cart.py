from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/cart", tags=["Cart"])

@router.post("/")
def create_cart(cart: schemas.CartCreate, db: Session = Depends(get_db)):
    new_cart = models.Cart(**cart.dict())
    db.add(new_cart)
    db.commit()
    db.refresh(new_cart)
    return new_cart


@router.post("/item")
def add_item(item: schemas.CartItemCreate, db: Session = Depends(get_db)):
    new_item = models.CartItem(**item.dict())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


@router.get("/{cart_id}")
def get_cart_items(cart_id: int, db: Session = Depends(get_db)):
    return db.query(models.CartItem).filter(models.CartItem.cart_id == cart_id).all()