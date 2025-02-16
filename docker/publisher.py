import pika
import json
import uuid

# Establish connection to RabbitMQ on localhost
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Declare a durable queue (will survive server restarts)
channel.queue_declare(queue='task_queue', durable=True)

# Prepare a sample message – "data" contains the prompt for model inference
message = {
    "task_id": str(uuid.uuid4()),
    "data": "Hello world. Please generate a short story about a brave knight.",
    "params": {"model": "gpt2", "options": {}}
}
message_body = json.dumps(message)

# Publish the message with persistent delivery mode
channel.basic_publish(
    exchange='',
    routing_key='task_queue',
    body=message_body,
    properties=pika.BasicProperties(
        delivery_mode=2  # persistent message
    )
)

print(f"Wysłano zadanie: {message['task_id']}")
connection.close()

