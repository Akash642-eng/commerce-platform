from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from uuid import uuid4


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/")
def get_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()


@router.post("/address")
def add_address(address: schemas.AddressCreate, db: Session = Depends(get_db)):
    new_address = models.Address(**address.dict())
    db.add(new_address)
    db.commit()
    db.refresh(new_address)
    return new_address


@router.get("/address/{user_id}")
def get_addresses(user_id: str, db: Session = Depends(get_db)):
    return db.query(models.Address).filter(models.Address.user_id == user_id).all()