import pika
import time
import json
import sys
import os

# Wybór modelu: można przekazać jako argument wiersza poleceń lub ustawić zmienną środowiskową MODEL_NAME.
# Domyślnie ustawiamy na "qwen".
if len(sys.argv) > 1:
    model_choice = sys.argv[1].lower()
else:
    model_choice = os.getenv("MODEL_NAME", "qwen").lower()

if model_choice == "qwen":
    from models import qwen as model_module
    print("Wybrano model Qwen.")
elif model_choice == "gpt2":
    from models import gpt2 as model_module
    print("Wybrano model GPT-2.")
else:
    raise ValueError("Nieobsługiwany model. Wybierz 'qwen' lub 'gpt2'.")

def callback(ch, method, properties, body):
    try:
        # Komunikat w formacie "task_id|prompt"
        decoded = body.decode()
        parts = decoded.split('|', 1)
        if len(parts) != 2:
            raise ValueError("Invalid message format. Expected 'task_id|prompt'.")
        task_id, prompt = parts[0], parts[1]
        print(f"Przetwarzam zadanie: {task_id} z promptem: {prompt}")
        
        # Przetwarzamy prompt przy użyciu wybranego modelu
        result = model_module.process_prompt(prompt)
        
        # Format wyjściowy: "task_id|result"
        output_message = f"{task_id}|{result}"
        channel.basic_publish(
            exchange='',
            routing_key='result_queue',
            body=output_message,
            properties=pika.BasicProperties(delivery_mode=2)
        )
        print(f"Wysłano wynik dla zadania: {task_id}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Błąd przy przetwarzaniu zadania {parts[0] if len(parts) > 0 else 'unknown'}: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='task_queue', durable=True)
channel.queue_declare(queue='result_queue', durable=True)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='task_queue', on_message_callback=callback, auto_ack=False)

print('Oczekiwanie na zadania. Aby zakończyć naciśnij CTRL+C')
channel.start_consuming()
