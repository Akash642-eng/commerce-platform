import pika
import os

def start_consumer():
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")

    print("Connecting to RabbitMQ at", rabbitmq_host)

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitmq_host)
    )

    channel = connection.channel()
    channel.queue_declare(queue='order_events')

    print("Waiting for order events...")

    def callback(ch, method, properties, body):
        print("Received order event:", body)

    channel.basic_consume(
        queue='order_events',
        on_message_callback=callback,
        auto_ack=True
    )

    channel.start_consuming()