import pika
import json
from vllm import LLM, SamplingParams
from transformers import AutoProcessor

# --- Inicjalizacja modelu ---
print("Ładowanie modelu (gpt2) na GPU...")
# Ładujemy model na GPU (cuda) przy użyciu torch.float16 (lub "auto")
engine = LLM("gpt2", dtype="auto", device="cuda")
print("Model został załadowany.")

# Jeśli używasz też procesora (dla tokenizacji i przygotowania danych wizualnych),
# możesz go załadować z opcją use_fast=True (jeśli model został zapisany z szybkim procesorem)
processor = AutoProcessor.from_pretrained("gpt2", use_fast=True)

def process_task(task):
    """
    Przetwarza zadanie, wykorzystując pole "data" jako prompt.
    W tym przykładzie używamy modelu vLLM do generowania wyniku.
    """
    prompt = task.get("data", "Hello world")
    print(f"Przetwarzam zadanie: {task['task_id']} z promptem: {prompt}")
    
    # Definicja parametrów samplingowych – można je modyfikować
    sampling_params = SamplingParams(n=1, temperature=1.0)
    # Generujemy wynik przy użyciu modelu
    result = engine.generate(prompt, sampling_params)
    
    # Zwracamy wynik w prostym formacie (np. jako string)
    return {
        "task_id": task["task_id"],
        "result": result
    }

# --- Konfiguracja RabbitMQ ---
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Deklarujemy kolejki jako trwałe
channel.queue_declare(queue='task_queue', durable=True)
channel.queue_declare(queue='result_queue', durable=True)

def callback(ch, method, properties, body):
    try:
        # Zakładamy, że komunikat jest w formacie JSON
        task = json.loads(body)
        # Przetwarzamy zadanie
        result = process_task(task)
        # Publikujemy wynik do kolejki result_queue
        channel.basic_publish(
            exchange='',
            routing_key='result_queue',
            body=json.dumps(result),
            properties=pika.BasicProperties(
                delivery_mode=2  # persistent message
            )
        )
        print(f"Wysłano wynik dla zadania: {result['task_id']}")
        # Ręczne potwierdzenie odbioru komunikatu
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Błąd przy przetwarzaniu zadania {task.get('task_id', 'unknown')}: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

# Ustawiamy prefetch, żeby worker przetwarzał jedno zadanie na raz
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='task_queue', on_message_callback=callback, auto_ack=False)

print('Oczekiwanie na zadania. Aby zakończyć naciśnij CTRL+C')
channel.start_consuming()

