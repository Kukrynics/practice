import feedparser
import requests
from typing import List
from pydantic import BaseModel
import asyncio


class TextItem(BaseModel):
    link: str
    text: str
    description: str


async def parse_rss_feed_async(urls: List[str]) -> None:
    items = []

    for url in urls:
        feed = feedparser.parse(url)  # Обрабатываем каждый URL отдельно
        items.extend(
            [TextItem(link=entry.link, text=entry.title, description=entry.description) for entry in feed.entries])

    # Переводим тексты с помощью API
    translated_items = await fetch_translated_rss(items)

    for original, translated in zip(items, translated_items):
        # Печатаем сначала оригинальный текст
        print(f"Original Link: {original.link}")
        print(f"Original Title: {original.text}")
        print(f"Original Description: {original.description}")

        # Печатаем перевод
        print(f"Translated Title: {translated.text}")
        print(f"Translated Description: {translated.description}")
        print("\n" + "="*50 + "\n")


async def fetch_translated_rss(rss_items: List[TextItem]) -> List[TextItem]:
    url = "http://127.0.0.1:8000/translate"

    try:
        response = await asyncio.to_thread(requests.post, url, json=[item.dict() for item in rss_items])

        if response.status_code == 200:
            translated_items = response.json()
            return [TextItem(link=item['link'], text=item['text'], description=item['description']) for item in translated_items]
        else:
            raise Exception(f"Ошибка при обращении к API перевода: {response.status_code}")
    except Exception as e:
        raise Exception(f"Ошибка при обращении к API перевода: {e}")