import pika
import json
import os
import time

from .logger import log_event  # ✅ NEW

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")


def publish_inventory_event(data, trace_id):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST)
    )
    channel = connection.channel()

    event = {
        "version": "v1",
        "order_id": data["order_id"],
        "status": "RESERVED"
    }

    channel.queue_declare(queue="inventory_reserved", durable=True)

    channel.basic_publish(
        exchange='',
        routing_key="inventory_reserved",
        body=json.dumps(event),
        properties=pika.BasicProperties(
            delivery_mode=2,
            headers={"x-trace-id": trace_id}  # ✅ propagate trace
        )
    )

    log_event("inventory-service", trace_id, "Sent inventory_reserved", event)

    connection.close()


def callback(ch, method, properties, body):
    try:
        data = json.loads(body)

        trace_id = properties.headers.get("x-trace-id") if properties.headers else "N/A"

        log_event("inventory-service", trace_id, "Inventory received order", data)

        time.sleep(1)

        publish_inventory_event(data, trace_id)

        ch.basic_ack(delivery_tag=method.delivery_tag)

        log_event("inventory-service", trace_id, "Inventory reserved", data)

    except Exception as e:
        log_event("inventory-service", trace_id, "Inventory error", {"error": str(e)}, level="ERROR")


def start_consumer():
    log_event("inventory-service", "SYSTEM", "Inventory consumer started")

    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST)
            )

            channel = connection.channel()

            channel.queue_declare(queue="order_created", durable=True)
            channel.queue_declare(queue="inventory_reserved", durable=True)

            channel.basic_consume(
                queue="order_created",
                on_message_callback=callback,
                auto_ack=False
            )

            log_event("inventory-service", "SYSTEM", "Waiting for order_created")

            channel.start_consuming()

        except Exception as e:
            log_event("inventory-service", "SYSTEM", "Retry error", {"error": str(e)}, level="ERROR")
            log_event("inventory-service", "SYSTEM", "Retrying in 5 seconds", level="WARNING")
            time.sleep(5)