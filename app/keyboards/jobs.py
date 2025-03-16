from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


async def generate_jobs_keyboard(job_openings):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=job.title, callback_data=f"job_{job.id}") for job in job_openings]
    ])
    return keyboard


async def generate_job_keyboard_for_questionnaire(job):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Создать анкету", callback_data=f'questionnaire_job_{job.id}')]
    ])
    return keyboard


keyboard_start_questionnaire = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Начать анкетирование", callback_data="start_questionnaire_1")]
])
