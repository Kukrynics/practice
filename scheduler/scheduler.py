# scheduler/scheduler.py
import schedule
import time
import asyncio
from parsers.rss_parser import parse_rss
from parsers.telegram_parser import parse_telegram

def job():
    # Пример использования RSS-канала
    rss_urls = ['https://example.com/rss']  # Добавьте свои RSS-каналы
    for url in rss_urls:
        parse_rss(url)

    # Пример использования Telegram-канала
    telegram_channels = ['example_channel']  # Добавьте свои Telegram-каналы
    loop = asyncio.get_event_loop()
    for channel in telegram_channels:
        loop.run_until_complete(parse_telegram(channel))

schedule.every(5).hours.do(job)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

