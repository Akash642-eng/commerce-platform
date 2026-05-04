import pika
import json
import os
import time

from .logger import log_event

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")

MAX_RETRIES = 3


def publish_to_queue(queue_name, message, trace_id, headers=None):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST)
    )
    channel = connection.channel()

    channel.queue_declare(queue=queue_name, durable=True)

    final_headers = headers or {}
    final_headers["x-trace-id"] = trace_id

    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2,
            headers=final_headers
        )
    )

    connection.close()


def publish_inventory_event(data, trace_id):
    event = {
        "version": "v1",
        "order_id": data["order_id"],
        "status": "RESERVED"
    }

    publish_to_queue("inventory_reserved", event, trace_id)

    log_event("inventory-service", trace_id, "Sent inventory_reserved", event)


def callback(ch, method, properties, body):
    trace_id = "N/A"

    try:
        data = json.loads(body)

        headers = properties.headers or {}
        retry_count = headers.get("x-retry", 0)
        trace_id = headers.get("x-trace-id", "N/A")

        log_event(
            "inventory-service",
            trace_id,
            f"Inventory received order (retry={retry_count})",
            data
        )

        time.sleep(1)

        publish_inventory_event(data, trace_id)

        ch.basic_ack(delivery_tag=method.delivery_tag)

        log_event("inventory-service", trace_id, "Inventory reserved", data)

    except Exception as e:
        log_event(
            "inventory-service",
            trace_id,
            "Inventory error",
            {"error": str(e)},
            level="ERROR"
        )

        headers = properties.headers or {}
        retry_count = headers.get("x-retry", 0)

        if retry_count < MAX_RETRIES:
            new_headers = headers.copy()
            new_headers["x-retry"] = retry_count + 1

            log_event(
                "inventory-service",
                trace_id,
                f"Retrying message ({retry_count + 1})",
                {},
                level="WARNING"
            )

            publish_to_queue(
                "order_created",
                json.loads(body),
                trace_id,
                headers=new_headers
            )

        else:
            log_event(
                "inventory-service",
                trace_id,
                "Sending to DLQ",
                {},
                level="ERROR"
            )

            publish_to_queue(
                "order_created_dlq",
                json.loads(body),
                trace_id,
                headers=headers
            )

        ch.basic_ack(delivery_tag=method.delivery_tag)


def start_consumer():
    log_event("inventory-service", "SYSTEM", "Inventory consumer started")

    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST)
            )

            channel = connection.channel()

            channel.queue_declare(queue="order_created", durable=True)
            channel.queue_declare(queue="order_created_dlq", durable=True)
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