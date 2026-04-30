from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
import pika
import json
import os

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")

router = APIRouter(prefix="/orders", tags=["Orders"])


def publish_event(queue, data, trace_id):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST)
    )
    channel = connection.channel()

    channel.queue_declare(queue=queue, durable=True)

    channel.basic_publish(
        exchange='',
        routing_key=queue,
        body=json.dumps(data),
        properties=pika.BasicProperties(
            delivery_mode=2,
            headers={"x-trace-id": trace_id}   # ✅ ROOT TRACE
        )
    )

    print(f"[TRACE {trace_id}] 🚀 Published {queue}: {data}", flush=True)

    connection.close()


@router.post("/")
def create_order(order: schemas.OrderCreate, request: Request, db: Session = Depends(get_db)):

    trace_id = request.headers.get("x-trace-id", "N/A")

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

    db.commit()

    publish_event("order_created", {
        "order_id": new_order.id,
        "user_id": str(new_order.user_id),
        "amount": float(new_order.total_amount)
    }, trace_id)

    return {"order_id": new_order.id, "status": "CREATED"}


@router.get("/")
def get_orders(db: Session = Depends(get_db)):
    return db.query(models.Order).all()