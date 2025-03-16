from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

refactoring = InlineKeyboardButton(text='Изменить данные', callback_data='refactoring_button')

profile_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [refactoring]
])
