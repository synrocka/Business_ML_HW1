import pika
import json
import os
import csv
from pathlib import Path

# Создаем директорию logs, если она не существует
Path("logs").mkdir(exist_ok=True)

# Создаем/открываем CSV файл и записываем заголовки, если файл новый
csv_path = "logs/metric_log.csv"
is_new_file = not os.path.exists(csv_path)

with open(csv_path, "a", newline="") as f:
    writer = csv.writer(f)
    if is_new_file:
        writer.writerow(["id", "y_true", "y_pred", "absolute_error"])

# Словари для хранения промежуточных значений
y_true_dict = {}
y_pred_dict = {}

try:
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
    channel = connection.channel()

    channel.queue_declare(queue="y_true")
    channel.queue_declare(queue="y_pred")

    def process_metrics(message_id):
        """Обработка и запись метрик, если доступны оба значения"""
        if message_id in y_true_dict and message_id in y_pred_dict:
            y_true = y_true_dict[message_id]
            y_pred = y_pred_dict[message_id]
            absolute_error = abs(y_true - y_pred)

            # Записываем метрики в CSV
            with open(csv_path, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([message_id, y_true, y_pred, absolute_error])

            # Очищаем обработанные значения
            del y_true_dict[message_id]
            del y_pred_dict[message_id]

            print(f"Метрики записаны для id: {message_id}, AE: {absolute_error}")

    def callback(ch, method, properties, body):
        message = json.loads(body)
        message_id = message["id"]
        value = message["value"]

        print(
            f"Из очереди {method.routing_key} получено значение {value} (id: {message_id})"
        )

        # Сохраняем значение в соответствующий словарь
        if method.routing_key == "y_true":
            y_true_dict[message_id] = value
        elif method.routing_key == "y_pred":
            y_pred_dict[message_id] = value

        # Пробуем обработать метрики
        process_metrics(message_id)

    channel.basic_consume(queue="y_true", on_message_callback=callback, auto_ack=True)
    channel.basic_consume(queue="y_pred", on_message_callback=callback, auto_ack=True)

    print("...Ожидание сообщений, для выхода нажмите CTRL+C")
    channel.start_consuming()
except Exception as e:
    print(f"Не удалось подключиться к очереди: {str(e)}")
