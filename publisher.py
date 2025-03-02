import pika
import uuid

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
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
