from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..logger import log_event

router = APIRouter(prefix="/deliveries", tags=["Deliveries"])


@router.post("/agent", response_model=schemas.DeliveryAgentResponse)
def create_agent(agent: schemas.DeliveryAgentCreate, db: Session = Depends(get_db)):

    new_agent = models.DeliveryAgent(**agent.dict())

    db.add(new_agent)

    db.commit()

    db.refresh(new_agent)

    log_event(
        service="delivery-service",
        trace_id=f"agent-{new_agent.id}",
        message="Delivery agent created",
        data={"agent_id": new_agent.id},
    )

    return new_agent


@router.post("/", response_model=schemas.DeliveryResponse)
def assign_delivery(delivery: schemas.DeliveryCreate, db: Session = Depends(get_db)):

    agent = (
        db.query(models.DeliveryAgent)
        .filter(models.DeliveryAgent.id == delivery.delivery_agent_id)
        .first()
    )

    if not agent:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Delivery agent not found"
        )

    new_delivery = models.Delivery(
        order_id=delivery.order_id,
        delivery_agent_id=delivery.delivery_agent_id,
        status="ASSIGNED",
        assigned_at=datetime.utcnow(),
    )

    db.add(new_delivery)

    db.commit()

    db.refresh(new_delivery)

    log_event(
        service="delivery-service",
        trace_id=f"delivery-{new_delivery.id}",
        message="Delivery assigned",
        data={"order_id": delivery.order_id, "agent_id": delivery.delivery_agent_id},
    )

    return new_delivery


@router.put("/deliver/{order_id}")
def mark_delivered(order_id: int, db: Session = Depends(get_db)):

    delivery = (
        db.query(models.Delivery).filter(models.Delivery.order_id == order_id).first()
    )

    if not delivery:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Delivery not found"
        )

    delivery.status = "DELIVERED"

    delivery.delivered_at = datetime.utcnow()

    db.commit()

    log_event(
        service="delivery-service",
        trace_id=f"delivery-{delivery.id}",
        message="Order delivered",
        data={"order_id": order_id},
    )

    return {"message": "Order delivered successfully", "order_id": order_id}


@router.get("/{order_id}", response_model=schemas.DeliveryResponse)
def get_delivery(order_id: int, db: Session = Depends(get_db)):

    delivery = (
        db.query(models.Delivery).filter(models.Delivery.order_id == order_id).first()
    )

    if not delivery:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Delivery not found"
        )

    return delivery
