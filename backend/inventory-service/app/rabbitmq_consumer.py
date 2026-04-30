import pika
import json
import os
import time

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
            headers={"x-trace-id": trace_id}   # ✅ FIX
        )
    )

    print(f"[TRACE {trace_id}] 📦 Sent inventory_reserved: {event}", flush=True)

    connection.close()


def callback(ch, method, properties, body):
    try:
        data = json.loads(body)

        trace_id = "N/A"
        if properties and properties.headers:
            trace_id = properties.headers.get("x-trace-id", "N/A")

        print(f"[TRACE {trace_id}] 📥 Inventory received: {data}", flush=True)

        time.sleep(1)

        publish_inventory_event(data, trace_id)

        ch.basic_ack(delivery_tag=method.delivery_tag)

        print(f"[TRACE {trace_id}] ✅ Inventory reserved", flush=True)

    except Exception as e:
        print("❌ Inventory error:", str(e), flush=True)


def start_consumer():
    print("🚀 Inventory consumer started", flush=True)

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

            print("📡 Waiting for order_created...", flush=True)
            channel.start_consuming()

        except Exception as e:
            import traceback
            print("❌ Retry ERROR:", repr(e), flush=True)
            traceback.print_exc()
            time.sleep(5)