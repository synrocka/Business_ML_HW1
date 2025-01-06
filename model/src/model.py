import pika
import pickle
import numpy as np
import json

# Читаем файл с сериализованной моделью
with open("myfile.pkl", "rb") as pkl_file:
    regressor = pickle.load(pkl_file)

try:
    # Создаём подключение по адресу rabbitmq:
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
    channel = connection.channel()

    # Объявляем очередь features
    channel.queue_declare(queue="features")
    # Объявляем очередь y_pred
    channel.queue_declare(queue="y_pred")

    # Создаём функцию callback для обработки данных из очереди
    def callback(ch, method, properties, body):
        message = json.loads(body)
        print(f'Получен вектор признаков (id: {message["id"]})')

        # Делаем предсказание
        features = np.array(message["value"]).reshape(1, -1)
        pred = regressor.predict(features)

        # Формируем сообщение с предсказанием
        prediction_message = {"id": message["id"], "value": pred[0]}

        channel.basic_publish(
            exchange="", routing_key="y_pred", body=json.dumps(prediction_message)
        )
        print(f'Предсказание отправлено в очередь y_pred (id: {message["id"]})')

    # Извлекаем сообщение из очереди features
    channel.basic_consume(queue="features", on_message_callback=callback, auto_ack=True)
    print("...Ожидание сообщений, для выхода нажмите CTRL+C")

    # Запускаем режим ожидания прихода сообщений
    channel.start_consuming()
except Exception as e:
    print(f"Не удалось подключиться к очереди: {str(e)}")
