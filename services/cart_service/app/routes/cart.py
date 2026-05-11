from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from sqlalchemy.orm import Session

from ..database import get_db
from .. import models
from .. import schemas


router = APIRouter(
    prefix="/cart",
    tags=["Cart"]
)


# --------------------------------
# CREATE CART
# --------------------------------
@router.post(
    "/",
    response_model=schemas.CartResponse
)
def create_cart(
    cart: schemas.CartCreate,
    db: Session = Depends(get_db)
):

    new_cart = models.Cart(
        user_id=cart.user_id
    )

    db.add(new_cart)
    db.commit()
    db.refresh(new_cart)

    return new_cart


# --------------------------------
# ADD ITEM TO CART
# --------------------------------
@router.post(
    "/{cart_id}/item",
    response_model=schemas.CartItemResponse
)
def add_item(
    cart_id: int,
    item: schemas.CartItemCreate,
    db: Session = Depends(get_db)
):

    cart = db.query(models.Cart).filter(
        models.Cart.id == cart_id
    ).first()

    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )

    existing_item = db.query(models.CartItem).filter(
        models.CartItem.cart_id == cart_id,
        models.CartItem.product_id == item.product_id
    ).first()

    # Increase quantity if already exists
    if existing_item:
        existing_item.quantity += item.quantity

        db.commit()
        db.refresh(existing_item)

        return existing_item

    new_item = models.CartItem(
        cart_id=cart_id,
        product_id=item.product_id,
        quantity=item.quantity
    )

    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return new_item


# --------------------------------
# GET CART
# --------------------------------
@router.get(
    "/{cart_id}",
    response_model=schemas.CartResponse
)
def get_cart(
    cart_id: int,
    db: Session = Depends(get_db)
):

    cart = db.query(models.Cart).filter(
        models.Cart.id == cart_id
    ).first()

    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )

    return cart


# --------------------------------
# DELETE CART ITEM
# --------------------------------
@router.delete(
    "/item/{item_id}"
)
def delete_cart_item(
    item_id: int,
    db: Session = Depends(get_db)
):

    item = db.query(models.CartItem).filter(
        models.CartItem.id == item_id
    ).first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )

    db.delete(item)
    db.commit()

    return {
        "message": "Cart item deleted"
    }