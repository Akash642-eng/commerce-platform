from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from datetime import datetime

router = APIRouter(prefix="/delivery", tags=["Delivery"])

@router.post("/agent")
def create_agent(agent: schemas.DeliveryAgentCreate, db: Session = Depends(get_db)):
    new_agent = models.DeliveryAgent(**agent.dict())
    db.add(new_agent)
    db.commit()
    db.refresh(new_agent)
    return new_agent


@router.post("/")
def assign_delivery(delivery: schemas.DeliveryCreate, db: Session = Depends(get_db)):
    new_delivery = models.Delivery(
        order_id=delivery.order_id,
        delivery_agent_id=delivery.delivery_agent_id,
        status="ASSIGNED",
        assigned_at=datetime.utcnow()
    )
    db.add(new_delivery)
    db.commit()
    db.refresh(new_delivery)
    return new_delivery


@router.put("/deliver/{order_id}")
def mark_delivered(order_id: int, db: Session = Depends(get_db)):
    delivery = db.query(models.Delivery).filter(models.Delivery.order_id == order_id).first()
    delivery.status = "DELIVERED"
    delivery.delivered_at = datetime.utcnow()
    db.commit()
    return {"status": "DELIVERED"}