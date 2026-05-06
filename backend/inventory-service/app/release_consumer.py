import pika
import json
import os
import time

from .logger import log_event

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")


def get_connection():
    while True:
        try:
            return pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=RABBITMQ_HOST,
                    heartbeat=600,
                    blocked_connection_timeout=300
                )
            )
        except:
            log_event("inventory-service", "system", "Failed to connect to RabbitMQ", {}, level="ERROR")
            time.sleep(5)


def callback(ch, method, properties, body):
    try:
        data = json.loads(body)

        log_event("inventory-service", "system", "Inventory release received", data)

        time.sleep(1)

        log_event("inventory-service", "system", f"Stock released for order {data['order_id']}", {})

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        log_event("inventory-service", "system", "Error occurred while processing inventory release", {"error": str(e)}, level="ERROR")


def start_release_consumer():
    log_event("inventory-service", "system", "Inventory release consumer started", {})

    while True:
        try:
            connection = get_connection()
            channel = connection.channel()

            channel.queue_declare(queue="inventory_release", durable=True)

            channel.basic_consume(
                queue="inventory_release",
                on_message_callback=callback,
                auto_ack=False
            )

            log_event("inventory-service", "system", "Waiting for inventory_release...", {})

            channel.start_consuming()

        except Exception as e:
            log_event("inventory-service", "system", "Error occurred while starting inventory release consumer", {"error": str(e)}, level="ERROR")
            time.sleep(5)