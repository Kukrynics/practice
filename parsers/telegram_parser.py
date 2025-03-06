# parsers/telegram_parser.py
import asyncio
import random
from telethon import TelegramClient
from database.queries import insert_news
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH


async def parse_telegram(channel):
    async with TelegramClient('session_name', TELEGRAM_API_ID, TELEGRAM_API_HASH) as client:
        async for message in client.iter_messages(channel):
            title = message.title or "No Title"
            content = message.message
            source = 'Telegram'
            url = f"https://t.me/{channel}/{message.id}"
            published_at = message.date

            # Вставка новости в базу данных
            insert_news(title, content, source, url, published_at)

            # Генерация случайной задержки от 1 до 10 секунд
            delay = random.uniform(1, 10)
            await asyncio.sleep(delay)  # Асинхронная задержка

