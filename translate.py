from fastapi import FastAPI
from pydantic import BaseModel
from deep_translator import GoogleTranslator
from typing import List

app = FastAPI()

# Default target language
target_language = 'ru'  # Default is Russian, can be updated dynamically


def set_target_language(language: str):
    global target_language
    target_language = language


class TextItem(BaseModel):
    link: str
    text: str
    description: str


class TranslatedTextItem(BaseModel):
    link: str
    text: str
    description: str


@app.post("/translate", response_model=List[TranslatedTextItem])
async def translate_texts(texts: List[TextItem]):
    translator = GoogleTranslator(source='auto', target=target_language)

    translated_texts = [
        TranslatedTextItem(
            link=item.link,
            text=translator.translate(item.text),
            description=translator.translate(item.description)
        )
        for item in texts
    ]
    return translated_texts


# Allow for dynamically setting the target language
set_target_language("ru")  # Initialize with default language