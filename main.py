# main.py
import logging

from database.models import create_tables
from scheduler.scheduler import run_scheduler, job

if __name__ == "__main__":
    create_tables()  # Создание таблиц в базе данных
    try:
        job()  # Запускаем парсинг сразу при старте
        run_scheduler()
    except KeyboardInterrupt:
        logging.info('Scheduler stopped.')

