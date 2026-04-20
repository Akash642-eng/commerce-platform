import pika
import json
import os

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")

def publish_event(queue, message):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST)
    )

    channel = connection.channel()
    channel.queue_declare(queue="order_created", durable=True)

    channel.basic_publish(
        exchange='',
        routing_key=queue,
        body=json.dumps(message)
    )

    connection.close()