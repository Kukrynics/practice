from aiogram import types, Dispatcher
from app.registration import cheek_registration


async def show_profile(message: types.Message):
    if message.text == 'Мой профиль':
        user = await cheek_registration(message)
        if user:
            await message.answer(f"Ваш профиль:\n"
                                 f"Имя: {user.first_name}\n"
                                 f"Фамилия: {user.last_name}\n"
                                 f"Отчество: {user.middle_name}\n"
                                 f"Телефон: {user.phone}\n"
                                 f"Дата рождения: {user.date_of_birth.strftime('%Y-%m-%d')}")
        else:
            await message.answer("Профиль не найден. Пожалуйста, зарегистрируйтесь.")


def register_profile_handlers(dp: Dispatcher):
    dp.message.register(show_profile, lambda message: message.text == 'Мой профиль')
