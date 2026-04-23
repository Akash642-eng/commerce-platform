import pika
import json
import os
import time
import random

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")


def publish_payment_event(ch, data):
    try:
        is_success = random.choice([True, False])

        if is_success:
            event = {
                "order_id": data["order_id"],
                "status": "SUCCESS"
            }

            ch.queue_declare(queue="payment_completed", durable=True)

            ch.basic_publish(
                exchange='',
                routing_key="payment_completed",
                body=json.dumps(event),
                properties=pika.BasicProperties(delivery_mode=2)
            )

            print("📤 Sent payment_completed event:", event, flush=True)

        else:
            event = {
                "order_id": data["order_id"],
                "status": "FAILED"
            }

            ch.queue_declare(queue="payment_failed", durable=True)

            ch.basic_publish(
                exchange='',
                routing_key="payment_failed",
                body=json.dumps(event),
                properties=pika.BasicProperties(delivery_mode=2)
            )

            print("❌ Sent payment_failed event:", event, flush=True)

    except Exception as e:
        print("❌ Failed to publish payment event:", str(e), flush=True)


def callback(ch, method, properties, body):
    try:
        data = json.loads(body)

        print("💳 Processing payment for order:", data["order_id"], flush=True)

        time.sleep(1)

        publish_payment_event(ch, data)

        ch.basic_ack(delivery_tag=method.delivery_tag)

        print("✅ Payment processed + ACK sent", flush=True)

    except Exception as e:
        print("❌ Failed processing:", str(e), flush=True)


def start_consumer():
    print("🚀 Payment consumer started", flush=True)

    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=RABBITMQ_HOST,
                    heartbeat=600,
                    blocked_connection_timeout=300
                )
            )

            channel = connection.channel()

            channel.queue_declare(queue="inventory_reserved", durable=True)
            channel.queue_declare(queue="payment_completed", durable=True)
            channel.queue_declare(queue="payment_failed", durable=True)

            channel.basic_qos(prefetch_count=1)

            channel.basic_consume(
                queue="inventory_reserved",
                on_message_callback=callback,
                auto_ack=False
            )

            print("📡 Waiting for inventory_reserved...", flush=True)
            channel.start_consuming()

        except Exception as e:
            import traceback
            print("❌ ERROR:", repr(e), flush=True)
            traceback.print_exc()
            print("🔁 Retrying in 5 seconds...", flush=True)
            time.sleep(5)