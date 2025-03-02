import pika
import json
import time

def process_task(task):
    """
    Simulates task processing.
    Replace the sleep with actual model integration if needed.
    """
    print(f"Przetwarzam zadanie: {task['task_id']}")
    time.sleep(3)  # Simulate a 3-second task processing time
    result = {
        "task_id": task["task_id"],
        "result": f"Wynik przetwarzania dla: {task['data']}"
    }
    return result

# Establish connection to RabbitMQ on localhost
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Declare the queues as durable
channel.queue_declare(queue='task_queue', durable=True)
channel.queue_declare(queue='result_queue', durable=True)

def callback(ch, method, properties, body):
    try:
        # Decode and load the message
        task = json.loads(body)
        # Process the task (simulate work or integrate your model here)
        result = process_task(task)
        # Publish the result to the result_queue as a persistent message
        channel.basic_publish(
            exchange='',
            routing_key='result_queue',
            body=json.dumps(result),
            properties=pika.BasicProperties(
                delivery_mode=pika.DeliveryMode.Persistent  # persistent result message
            )
        )
        print(f"Wysłano wynik dla zadania: {result['task_id']}")
        # Send manual acknowledgment to RabbitMQ after successful processing
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Błąd przy przetwarzaniu zadania: {e}")
        # If processing fails, reject the message and ask RabbitMQ to requeue it
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

# Set QoS so the worker processes only one message at a time
channel.basic_qos(prefetch_count=1)
# Consume messages with manual acknowledgment (auto_ack set to False)
channel.basic_consume(queue='task_queue', on_message_callback=callback, auto_ack=False)

print('Oczekiwanie na zadania. Aby zakończyć naciśnij CTRL+C')
channel.start_consuming()

