from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from ..rabbitmq_producer import publish_event


router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/")
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    new_order = models.Order(
        user_id=order.user_id,
        total_amount=order.total_amount,
        status="CREATED"
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    for item in order.items:
        order_item = models.OrderItem(
            order_id=new_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.price
        )
        db.add(order_item)

    status = models.OrderStatusHistory(
        order_id=new_order.id,
        status="CREATED"
    )
    db.add(status)

    db.commit()

    # Send event to RabbitMQ
    publish_event("order_created", {
        "order_id": new_order.id,
        "user_id": str(new_order.user_id),
        "amount": float(new_order.total_amount)
    })

    return {"order_id": new_order.id, "status": "CREATED"}


@router.get("/")
def get_orders(db: Session = Depends(get_db)):
    return db.query(models.Order).all()