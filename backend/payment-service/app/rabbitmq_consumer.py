import pika
import json
import os
import time

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")


def publish_payment_event(channel, data):
    """
    Publish payment result back to RabbitMQ
    """
    event = {
        "order_id": data["order_id"],
        "status": "SUCCESS"
    }

    channel.queue_declare(queue="payment_completed", durable=True)

    channel.basic_publish(
        exchange='',
        routing_key="payment_completed",
        body=json.dumps(event),
        properties=pika.BasicProperties(
            delivery_mode=2  
        )
    )

    print("📤 Sent payment_completed event:", event, flush=True)


def callback(ch, method, properties, body):
    try:
        data = json.loads(body)

        print("✅ Received order event:", data, flush=True)
        print("💳 Processing payment for order:", data["order_id"], flush=True)

        time.sleep(1)

        publish_payment_event(ch, data)

    
        ch.basic_ack(delivery_tag=method.delivery_tag)

        print("✅ Payment processed + ACK sent", flush=True)

    except Exception as e:
        print("❌ Failed processing:", str(e), flush=True)


def start_consumer():
    print("🚀 Consumer function ENTERED", flush=True)

    while True:
        try:
            print("🔌 Trying to connect to RabbitMQ...", flush=True)

            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=RABBITMQ_HOST,
                    heartbeat=600,
                    blocked_connection_timeout=300
                )
            )

            print("✅ Connected to RabbitMQ", flush=True)

            channel = connection.channel()

            channel.queue_declare(queue="order_created", durable=True)

            channel.basic_qos(prefetch_count=1)

            channel.basic_consume(
                queue="order_created",
                on_message_callback=callback,
                auto_ack=False
            )

            print("📡 Waiting for order events...", flush=True)
            channel.start_consuming()

        except Exception as e:
            print("❌ ERROR in consumer:", str(e), flush=True)

            import traceback
            traceback.print_exc()

            print("🔁 Retrying in 5 seconds...", flush=True)
            time.sleep(5)