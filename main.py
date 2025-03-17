import time
import asyncio
import multiprocessing
import uvicorn
from rss_parser import parse_rss_feed_async


# Функция для запуска FastAPI-сервера для перевода
def run_translate_server(target_language: str):
    import translate  # Импортируем файл с API
    translate.set_target_language(target_language)  # Устанавливаем целевой язык
    uvicorn.run(translate.app, host="127.0.0.1", port=8000)


# Функция для запуска основного процесса
async def run_main():
    rss_urls = [
        "https://www.cbsnews.com/latest/rss/us",
        "https://rss.haberler.com/rss.asp?kategori=sondakika"
    ]

    while True:
        # Периодический парсинг RSS лент
        await parse_rss_feed_async(rss_urls)
        print("\n" + "=" * 50 + "\n")
        await asyncio.sleep(60)  # Интервал для обновления RSS (например, 60 секунд)


if __name__ == '__main__':
    target_language = input("Введите целевой язык для перевода (например, 'ru' для русского): ").strip()

    # Запускаем сервер перевода в отдельном процессе
    server_process = multiprocessing.Process(target=run_translate_server, args=(target_language,))
    server_process.start()

    # Пауза, чтобы сервер успел запуститься
    time.sleep(3)

    # Запускаем основной процесс
    asyncio.run(run_main())

    # Ожидание завершения серверного процесса
    server_process.join()