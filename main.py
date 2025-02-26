# -*- coding: utf-8 -*-
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from deep_translator import GoogleTranslator
import time
import asyncio
import multiprocessing
import uvicorn
import feedparser

app = FastAPI()
translator = GoogleTranslator(source='auto', target='ru')

class TextItem(BaseModel):
    link: str
    text: str

class TranslatedTextItem(BaseModel):
    link: str
    text: str

@app.post("/translate", response_model=List[TranslatedTextItem])
async def translate_texts(texts: List[TextItem]):
    translated_texts = [
        TranslatedTextItem(link=item.link, text=translator.translate(item.text))
        for item in texts
    ]
    return translated_texts

# Функция для парсинга RSS-ленты и извлечения заголовков и ссылок.
def parse_rss_feed(url):
    """
    Функция для парсинга RSS-ленты и перевода заголовков.
    :param url: URL RSS-ленты
    :return: Список объектов с полями link и text
    """
    feed = feedparser.parse(url)
    items = [TextItem(link=entry.link, text=entry.title) for entry in feed.entries]
    return items

# Объединенная функция для получения и перевода RSS-заголовков
async def fetch_and_translate_rss(url):
    rss_items = parse_rss_feed(url)
    translated_items = await translate_texts(rss_items)
    return translated_items

# Функция для запуска FastAPI
def run_server():
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == '__main__':
    server_process = multiprocessing.Process(target=run_server)
    server_process.start()

    # Пауза, чтобы сервер успел запуститься
    time.sleep(3)

    rss_url = "https://rss.haberler.com/rss.asp?kategori=sondakika"  # Замените на реальный URL RSS
    translated_news = asyncio.run(fetch_and_translate_rss(rss_url))
    for news in translated_news:
        print(news)


    # Ожидание завершения серверного процесса
    server_process.join()
