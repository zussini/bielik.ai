import pika
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

# Pobieramy adres IP z zmiennej środowiskowej, domyślnie 'localhost'
rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
rabbitmq_port = os.getenv("RABBITMQ_PORT", 5672)
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host,port=rabbitmq_port))
channel = connection.channel()

channel.queue_declare(queue='task_queue', durable=True)

task_id = str(uuid.uuid4())
prompt = "Write name of the composer of 'The Ecstasy of Gold'. Is it Ennio Morricone?"
message = f"{task_id}|{prompt}"

channel.basic_publish(
    exchange='',
    routing_key='task_queue',
    body=message,
    properties=pika.BasicProperties(delivery_mode=2)
)

print(f"Wysłano zadanie: {task_id}")
connection.close()
