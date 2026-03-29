from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/inventory", tags=["Inventory"])

@router.post("/")
def create_inventory(item: schemas.InventoryCreate, db: Session = Depends(get_db)):
    inv = models.Inventory(**item.dict())
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv


@router.get("/")
def get_inventory(db: Session = Depends(get_db)):
    return db.query(models.Inventory).all()


@router.post("/movement")
def stock_movement(move: schemas.StockMovementCreate, db: Session = Depends(get_db)):
    movement = models.StockMovement(**move.dict())
    db.add(movement)
    db.commit()
    db.refresh(movement)
    return movement