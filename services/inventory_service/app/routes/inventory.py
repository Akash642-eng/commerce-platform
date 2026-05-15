from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.post("/")
def create_inventory(item: schemas.InventoryCreate, db: Session = Depends(get_db)):

    inventory = models.Inventory(**item.dict())

    db.add(inventory)

    db.commit()

    db.refresh(inventory)

    return inventory


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
