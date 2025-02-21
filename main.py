from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from deep_translator import GoogleTranslator
import requests

app = FastAPI()
translator = GoogleTranslator(source='auto', target='ru')


class TextItem(BaseModel):
    id: int
    text: str


class TranslatedTextItem(BaseModel):
    id: int
    translated_text: str


@app.post("/translate", response_model=List[TranslatedTextItem])
def translate_texts(texts: List[TextItem]):
    translated_texts = [
        TranslatedTextItem(id=item.id, translated_text=translator.translate(item.text))
        for item in texts
    ]
    return translated_texts


# Отправка POST-запроса к /translate
def send_post_request():
    url = "http://127.0.0.1:8000/translate"
    data = [{"id": 1, "text": "Hello"},
            {"id": 2, "text": "mundo"},
            {"id": 3, "text": "人类"}]
    response = requests.post(url, json=data)
    print(response.json())


if __name__ == "__main__":
    send_post_request()