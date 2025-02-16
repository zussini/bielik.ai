import pika
import time
from vllm import LLM, SamplingParams

# --- Initialize the model engine once at startup ---
print("Ładowanie modelu (gpt2)...")
# Adjust device as needed ("cuda" for GPU, "cpu" for CPU)
engine = LLM("gpt2", dtype="auto")
print("Model został załadowany.")

def process_prompt(prompt):
    """
    Process the prompt using vLLM.
    Adjust the sampling parameters as needed.
    """
    sampling_params = SamplingParams(n=1, temperature=1.0)
    result = engine.generate(prompt, sampling_params)
    return result

# --- Setup RabbitMQ connection ---
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Declare the queues as durable
channel.queue_declare(queue='task_queue', durable=True)
channel.queue_declare(queue='result_queue', durable=True)

def callback(ch, method, properties, body):
    try:
        # The message is plain text in the format: "task_id|prompt"
        decoded = body.decode()
        parts = decoded.split('|', 1)
        if len(parts) != 2:
            raise ValueError("Invalid message format. Expected 'task_id|prompt'.")
        task_id, prompt = parts[0], parts[1]
        print(f"Przetwarzam zadanie: {task_id} z promptem: {prompt}")
        
        # Process the prompt using vLLM
        result = process_prompt(prompt)
        
        # Create output in plain text: "task_id|result"
        output_message = f"{task_id}|{result}"
        channel.basic_publish(
            exchange='',
            routing_key='result_queue',
            body=output_message,
            properties=pika.BasicProperties(delivery_mode=2)
        )
        print(f"Wysłano wynik dla zadania: {task_id}")
        # Send manual acknowledgment after successful processing
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Błąd przy przetwarzaniu zadania {parts[0] if len(parts) > 0 else 'unknown'}: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

# Ensure the worker processes only one message at a time
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='task_queue', on_message_callback=callback, auto_ack=False)

print('Oczekiwanie na zadania. Aby zakończyć naciśnij CTRL+C')
channel.start_consuming()

