import pika
import uuid

# Establish connection to RabbitMQ on localhost
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Declare a durable queue (will survive server restarts)
channel.queue_declare(queue='task_queue', durable=True)

# Prepare a sample message with task_id and prompt separated by a pipe
task_id = str(uuid.uuid4())
prompt = "Write name of the composer of Ecstasy of Gold. Is it Ennio Morricone?"
message = f"{task_id}|{prompt}"

# Publish the message with persistent delivery mode (2)
channel.basic_publish(
    exchange='',
    routing_key='task_queue',
    body=message,
    properties=pika.BasicProperties(delivery_mode=2)
)

print(f"Wysłano zadanie: {task_id}")
connection.close()

