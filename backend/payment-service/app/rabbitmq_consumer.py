import pika
import json
import os
import time
import random

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")


def publish_payment_event(data):
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST)
        )
        channel = connection.channel()

        is_success = random.choice([True, False])

        if is_success:
            event = {
                "order_id": data["order_id"],
                "status": "SUCCESS"
            }

            channel.queue_declare(queue="payment_completed", durable=True)

            channel.basic_publish(
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

            channel.queue_declare(queue="payment_failed", durable=True)

            channel.basic_publish(
                exchange='',
                routing_key="payment_failed",
                body=json.dumps(event),
                properties=pika.BasicProperties(delivery_mode=2)
            )

            print("❌ Sent payment_failed event:", event, flush=True)

        connection.close()

    except Exception as e:
        print("❌ Failed to publish payment event:", str(e), flush=True)

def publish_failed_event(event):
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST)
        )
        channel = connection.channel()

        channel.queue_declare(queue="payment_failed", durable=True)

        channel.basic_publish(
            exchange='',
            routing_key="payment_failed",
            body=json.dumps(event),
            properties=pika.BasicProperties(delivery_mode=2)
        )

        print("❌ Sent payment_failed event:", event, flush=True)

        connection.close()

    except Exception as e:
        print("❌ Failed to publish FAILED event:", str(e), flush=True)

def callback(ch, method, properties, body):
    try:
        data = json.loads(body)

        retry_count = data.get("retry", 0)

        print(f"📥 RECEIVED: {data} (retry={retry_count})", flush=True)

        print("💳 Processing payment for order:", data["order_id"], flush=True)

        if data["order_id"] % 5 == 0:
            raise Exception("Simulated payment failure")

        time.sleep(1)

        publish_payment_event(data)

        ch.basic_ack(delivery_tag=method.delivery_tag)

        print("✅ Payment processed + ACK sent", flush=True)

    except Exception as e:
        print("❌ Processing failed:", str(e), flush=True)

        retry_count = data.get("retry", 0)

        if retry_count >= 3:
            print("🚫 Max retries reached → sending FAILED event", flush=True)

            fail_event = {
                "order_id": data["order_id"],
                "status": "FAILED"
            }

            publish_failed_event(fail_event)

            ch.basic_ack(delivery_tag=method.delivery_tag)

        else:
            data["retry"] = retry_count + 1

            ch.basic_publish(
                exchange='',
                routing_key="inventory_reserved",
                body=json.dumps(data),
                properties=pika.BasicProperties(delivery_mode=2)
            )

            print(f"🔁 Retrying... ({data['retry']})", flush=True)

            ch.basic_ack(delivery_tag=method.delivery_tag)

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
            print("❌ ERROR:", str(e), flush=True)
            print("🔁 Retrying in 5 seconds...", flush=True)
            time.sleep(5)