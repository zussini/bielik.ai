import pika
import json
import uuid

# Połączenie z RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Deklaracja trwałej kolejki
channel.queue_declare(queue='task_queue', durable=True)

# Przygotowanie przykładowego komunikatu
message = {
    "task_id": str(uuid.uuid4()),
    "data": "WAAZAAAAAAAAAAAAAAAAA!!!!!!!",  # Prompt, który chcesz przetworzyć
    "params": {"model": "gpt2", "options": {}}
}
message_body = json.dumps(message)

# Wysyłamy komunikat z ustawieniem persistent (delivery_mode=2)
channel.basic_publish(
    exchange='',
    routing_key='task_queue',
    body=message_body,
    properties=pika.BasicProperties(
        delivery_mode=2
    )
)

print(f"Wysłano zadanie: {message['task_id']}")
connection.close()

