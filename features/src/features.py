import pika
import numpy as np
import json
from sklearn.datasets import load_diabetes
import time
from datetime import datetime

# Загружаем датасет о диабете один раз перед циклом
X, y = load_diabetes(return_X_y=True)

# Создаём бесконечный цикл для отправки сообщений в очередь
while True:
    try:
        # Формируем случайный индекс строки
        random_row = np.random.randint(0, X.shape[0] - 1)

        # Генерируем уникальный идентификатор на основе временной метки
        timestamp = datetime.now().timestamp()

        # Создаём подключение по адресу rabbitmq:
        connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
        channel = connection.channel()

        # Создаём очередь y_true
        channel.queue_declare(queue="y_true")
        # Создаём очередь features
        channel.queue_declare(queue="features")

        # Формируем сообщения с идентификаторами
        y_true_message = {"id": timestamp, "value": y[random_row]}

        features_message = {"id": timestamp, "value": list(X[random_row])}

        # Публикуем сообщение в очередь y_true
        channel.basic_publish(
            exchange="", routing_key="y_true", body=json.dumps(y_true_message)
        )
        print(f"Сообщение с правильным ответом отправлено в очередь (id: {timestamp})")

        # Публикуем сообщение в очередь features
        channel.basic_publish(
            exchange="", routing_key="features", body=json.dumps(features_message)
        )
        print(f"Сообщение с вектором признаков отправлено в очередь (id: {timestamp})")

        # Закрываем подключение
        connection.close()

        # Добавляем задержку в 5 секунд между итерациями
        time.sleep(5)

    except Exception as e:
        print(f"Не удалось подключиться к очереди: {str(e)}")
        # Добавляем задержку перед повторной попыткой подключения
        time.sleep(5)
