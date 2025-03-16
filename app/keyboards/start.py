from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


jobs = KeyboardButton(text='Вакансии')
my_profile = KeyboardButton(text='Мой профиль')
my_questionnaire = KeyboardButton(text='Последняя анкета')
all_questionnaires = KeyboardButton(text='Все мои анкеты')


keyboard_start = ReplyKeyboardMarkup(keyboard=[
    [jobs],
    [my_questionnaire, all_questionnaires],
    [my_profile]
], resize_keyboard=True)
