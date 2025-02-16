import pika
import json
from vllm import LLM, SamplingParams

# --- Initialize the model engine once at startup ---
print("Ładowanie modelu (gpt2)...")
# Adjust device as needed ("cuda" for GPU, "cpu" for CPU)
engine = LLM("gpt2", dtype="auto", device="cpu")
print("Model został załadowany.")

def process_task(task):
    """
    Process the task using the 'data' field as a prompt.
    Replace or extend this function with your actual model integration.
    """
    prompt = task.get("data", "Hello world")
    print(f"Przetwarzam zadanie: {task['task_id']} z promptem: {prompt}")
    
    # Define sampling parameters (adjust as needed)
    sampling_params = SamplingParams(n=1, temperature=1.0)
    
    # Generate model output using vLLM
    result = engine.generate(prompt, sampling_params)
    
    # Here we assume result is a list of outputs; adjust formatting as needed.
    return {
        "task_id": task["task_id"],
        "result": result
    }

# --- Setup RabbitMQ connection ---
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Declare the queues as durable
channel.queue_declare(queue='task_queue', durable=True)
channel.queue_declare(queue='result_queue', durable=True)

def callback(ch, method, properties, body):
    try:
        # Decode and parse the incoming message
        task = json.loads(body)
        # Process the task (e.g., perform model inference)
        result = process_task(task)
        
        # Publish the result to the result_queue as a persistent message
        channel.basic_publish(
            exchange='',
            routing_key='result_queue',
            body=json.dumps(result),
            properties=pika.BasicProperties(
                delivery_mode=pika.BasicProperties.PERSISTENT  # persistent message
            )
        )
        print(f"Wysłano wynik dla zadania: {result['task_id']}")
        # Send manual acknowledgment after successful processing
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Błąd przy przetwarzaniu zadania {task.get('task_id', 'unknown')}: {e}")
        # If processing fails, reject and requeue the message
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

# Set QoS so the worker processes one message at a time
channel.basic_qos(prefetch_count=1)
# Start consuming messages (with manual acknowledgment)
channel.basic_consume(queue='task_queue', on_message_callback=callback, auto_ack=False)

print('Oczekiwanie na zadania. Aby zakończyć naciśnij CTRL+C')
channel.start_consuming()

