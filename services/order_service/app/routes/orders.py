import uuid

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..logger import log_event
from ..rabbitmq_producer import publish_event

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


@router.post("/")
def create_order(
    order: schemas.OrderCreate,
    request: Request,
    db: Session = Depends(get_db),
):

    trace_id = request.headers.get(
        "x-trace-id"
    ) or str(uuid.uuid4())

    correlation_id = request.headers.get(
        "x-correlation-id"
    ) or trace_id

    saga_id = str(uuid.uuid4())

    new_order = models.Order(
        user_id=order.user_id,
        total_amount=order.total_amount,
        status="CREATED",
        payment_status="PENDING",
        saga_id=saga_id,
        correlation_id=correlation_id,
        event_version="v1",
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    for item in order.items:

        db.add(
            models.OrderItem(
                order_id=new_order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.price,
            )
        )

    db.commit()

    event = {
        "event_version": "v1",
        "order_id": new_order.id,
        "user_id": str(new_order.user_id),
        "amount": float(new_order.total_amount),
        "status": "CREATED",
        "trace_id": trace_id,
        "correlation_id": correlation_id,
        "saga_id": saga_id,
    }

    log_event(
        service="order-service",
        event="order_created",
        trace_id=trace_id,
        message="Saga started",
        data=event,
    )

    publish_event(
        queue="order_created",
        data=event,
        trace_id=trace_id,
        saga_id=saga_id,
        correlation_id=correlation_id,
        event_version="v1",
    )

    return {
        "order_id": new_order.id,
        "status": new_order.status,
        "payment_status": new_order.payment_status,
        "trace_id": trace_id,
        "correlation_id": correlation_id,
        "saga_id": saga_id,
        "event_version": "v1",
    }