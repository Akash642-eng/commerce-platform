import pika
import json
import os
import time
from .database import SessionLocal
from .models import Order
from .state_machine import can_transition

from .logger import log_event

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")

MAX_RETRIES = 3


def publish(queue, message, headers=None):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST)
    )
    channel = connection.channel()

    channel.queue_declare(queue=queue, durable=True)

    final_headers = headers.copy() if headers else {}

    channel.basic_publish(
        exchange='',
        routing_key=queue,
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2,
            headers=final_headers
        )
    )

    connection.close()


def publish_inventory_release(data, trace_id):
    event = {
        "order_id": data["order_id"],
        "status": "RELEASED"
    }

    publish(
        "inventory_release",
        event,
        headers={"x-trace-id": trace_id}
    )

    log_event("order-service", trace_id, "Sent inventory_release", event)


def callback(ch, method, properties, body):
    db = SessionLocal()
    trace_id = "unknown"

    try:
        data = json.loads(body)

        headers = properties.headers or {}
        trace_id = headers.get("x-trace-id", "unknown")
        retry_count = headers.get("x-retry", 0)
        
        log_event("order-service", trace_id, f"Payment failed received (retry={retry_count})", data)

        order = db.query(Order).filter(Order.id == data["order_id"]).first()

        if not order:
            log_event("order-service", trace_id, "Order not found", data, level="WARNING")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        if order.status == "FAILED":
            log_event("order-service", trace_id, f"Duplicate FAILED ignored for order {order.id}", data, level="WARNING")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        if can_transition(order.status, "FAILED"):
            order.status = "FAILED"
            db.commit()
            log_event("order-service", trace_id, f"Order {order.id} moved to FAILED", data)

            publish_inventory_release(data, trace_id)

        else:
            raise Exception(f"Invalid transition {order.status} → FAILED")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        log_event("order-service", trace_id, "Error processing payment failed event", {"error": str(e)}, level="ERROR")

        headers = properties.headers or {}
        retry_count = headers.get("x-retry", 0)

        if retry_count < MAX_RETRIES:
            new_headers = headers.copy()
            new_headers["x-retry"] = retry_count + 1
            new_headers["x-trace-id"] = trace_id  

            log_event("order-service", trace_id, f"Retrying... {retry_count + 1}", data)

            publish(
                "payment_failed",
                json.loads(body),
                headers=new_headers
            )

        else:
            log_event("order-service", trace_id, "Sending to DLQ", data)

            publish(
                "payment_failed_dlq",
                json.loads(body),
                headers=headers
            )

        ch.basic_ack(delivery_tag=method.delivery_tag)

    finally:
        db.close()


def start_failed_consumer():
    log_event("order-service", "SYSTEM", "Payment FAILED consumer started",{})

    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST)
            )

            channel = connection.channel()

            channel.queue_declare(queue="payment_failed", durable=True)
            channel.queue_declare(queue="payment_failed_dlq", durable=True)

            channel.basic_consume(
                queue="payment_failed",
                on_message_callback=callback,
                auto_ack=False
            )

            log_event("order-service", "SYSTEM", "Waiting for payment_failed events...",{})
            channel.start_consuming()

        except Exception as e:
            log_event("order-service", "SYSTEM", "Consumer retry", {"error": str(e)}, level="ERROR")
    
            time.sleep(5)