from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..logger import log_event
from ..rabbitmq_producer import publish_event

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/")
def create_order(
    order: schemas.OrderCreate, request: Request, db: Session = Depends(get_db)
):

    trace_id = request.headers.get("x-trace-id") or "unknown"

    new_order = models.Order(
        user_id=order.user_id, total_amount=order.total_amount, status="CREATED"
    )

    db.add(new_order)

    db.commit()

    db.refresh(new_order)

    for item in order.items:

        order_item = models.OrderItem(
            order_id=new_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.price,
        )

        db.add(order_item)

    db.commit()

    log_event(
        service="order-service",
        event="order_created",
        trace_id=trace_id,
        message="Order created",
        data={"order_id": new_order.id, "status": "CREATED"},
    )

    publish_event(
        "order_created",
        {
            "order_id": new_order.id,
            "user_id": str(new_order.user_id),
            "amount": float(new_order.total_amount),
        },
        trace_id,
    )

    return {"order_id": new_order.id, "status": "CREATED"}
