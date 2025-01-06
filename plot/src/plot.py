import pandas as pd
import matplotlib.pyplot as plt
import time
from pathlib import Path


def create_error_histogram(df):
    plt.figure(figsize=(10, 6))
    plt.hist(df["absolute_error"], bins=30, edgecolor="black")
    plt.title("Гистограмма абсолютных ошибок")
    plt.xlabel("Absolute Error")
    plt.ylabel("Frequency")
    plt.grid(True, alpha=0.3)
    plt.savefig("logs/error_distribution.png")
    plt.close()


def monitor_and_plot():
    last_modified = 0

    while True:
        try:
            # Проверяем, существует ли файл и его время модификации
            csv_path = Path("logs/metric_log.csv")
            if not csv_path.exists():
                print("Ожидаем создания файла metric_log.csv...")
                time.sleep(5)
                continue

            current_modified = csv_path.stat().st_mtime

            # Обновляем график, если файл был изменен
            if current_modified > last_modified:
                try:
                    print("Изменения обнаружены, обновляем график...")
                    df = pd.read_csv(csv_path)
                    if len(df) > 0:
                        create_error_histogram(df)
                        last_modified = current_modified
                        print("График успешно обновлен")
                    else:
                        print("Файл пуст, ожидаем данных...")
                except pd.errors.EmptyDataError:
                    print("Файл пуст, ожидаем данных...")
                except Exception as e:
                    print(f"Ошибка при создании графика: {e}")

            time.sleep(5)

        except Exception as e:
            print(f"Возникла ошибка: {e}")
            time.sleep(5)


if __name__ == "__main__":
    print("Запуск мониторинга метрик...")
    monitor_and_plot()
