import pika

def result_callback(ch, method, properties, body):
    message = body.decode()
    print("Otrzymano wiadomość:", message)
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='result_queue', durable=True)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='result_queue', on_message_callback=result_callback, auto_ack=False)

print("Czekam na wyniki. Aby zakończyć naciśnij CTRL+C")
channel.start_consuming()

