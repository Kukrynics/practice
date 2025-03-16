import re
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from aiogram import types, Dispatcher
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from sqlalchemy import insert, select
from app.utils.datebase import async_session_maker
from app.models.users import UserTelegram


class Registration(StatesGroup):
    first_name = State()
    last_name = State()
    middle_name = State()
    phone = State()
    date_of_birth = State()


async def start_registration(message: types.Message, state: FSMContext):
    user = await cheek_registration(message)
    if user:
        await message.answer(f"Вы уже зарегистрированы, {user.first_name} {user.middle_name}!")
        return
    await message.answer("Пожалуйста, введите ваше имя:")
    await state.set_state(Registration.first_name)


async def process_first_name(message: types.Message, state: FSMContext):
    name = message.text.strip()

    if not name.isalpha():
        await message.answer("Имя должно содержать только буквы. Пожалуйста, введите корректное имя:")
        return

    if len(name) < 2 or len(name) > 50:
        await message.answer("Имя должно быть длиной от 2 до 50 символов. Пожалуйста, введите корректное имя:")
        return

    await state.update_data(first_name=name.capitalize())
    await message.answer("Пожалуйста, введите вашу фамилию:")
    await state.set_state(Registration.last_name)


async def process_last_name(message: types.Message, state: FSMContext):
    last_name = message.text.strip()

    if not last_name.isalpha():
        await message.answer("Фамилия должна содержать только буквы. Пожалуйста, введите корректную фамилию:")
        return

    if len(last_name) < 2 or len(last_name) > 50:
        await message.answer("Фамилия должна быть длиной от 2 до 50 символов. Пожалуйста, введите корректную фамилию:")
        return

    await state.update_data(last_name=last_name.capitalize())
    await message.answer("Пожалуйста, введите ваше отчество:")
    await state.set_state(Registration.middle_name)


async def process_middle_name(message: types.Message, state: FSMContext):
    middle_name = message.text.strip()

    if not middle_name.isalpha():
        await message.answer("Отчество должно содержать только буквы. Пожалуйста, введите корректное отчество:")
        return

    if len(middle_name) < 2 or len(middle_name) > 50:
        await message.answer(
            "Отчество должно быть длиной от 2 до 50 символов. Пожалуйста, введите корректное отчество:")
        return

    await state.update_data(middle_name=middle_name.capitalize())
    await message.answer("Пожалуйста, введите ваш номер телефона (можно в любом формате):")
    await state.set_state(Registration.phone)


async def process_phone(message: types.Message, state: FSMContext):
    phone = message.text.strip()

    # Убираем все нецифровые символы для проверки
    digits_only = re.sub(r'\D', '', phone)

    # Проверяем длину и первую цифру
    if len(digits_only) not in [10, 11]:
        await message.answer("Номер телефона должен содержать 10 или 11 цифр. Пожалуйста, введите корректный номер:")
        return

    # Если номер начинается с 8 или 7, это российский номер
    if len(digits_only) == 11 and digits_only[0] in ['7', '8']:
        formatted_number = '+7(' + digits_only[1:4] + ')' + digits_only[4:7] + '-' + digits_only[
                                                                                     7:9] + '-' + digits_only[9:11]
    # Если 10 цифр, то добавляем +7
    elif len(digits_only) == 10:
        formatted_number = '+7(' + digits_only[0:3] + ')' + digits_only[3:6] + '-' + digits_only[
                                                                                     6:8] + '-' + digits_only[8:10]
    else:
        await message.answer("Введите номер российского телефона. Пожалуйста, попробуйте снова:")
        return

    await state.update_data(phone=formatted_number)
    await message.answer("Пожалуйста, введите вашу дату рождения (ГГГГ-ММ-ДД):")
    await state.set_state(Registration.date_of_birth)


async def process_date_of_birth(message: types.Message, state: FSMContext):
    date_string = message.text.strip()

    try:
        # Проверка формата даты
        birth_date = datetime.strptime(date_string, '%Y-%m-%d').date()

        # Проверка, что дата не в будущем
        if birth_date > date.today():
            await message.answer("Дата рождения не может быть в будущем. Пожалуйста, введите корректную дату:")
            return

        # Проверка возраста (должен быть не младше 14 и не старше 100 лет)
        age = relativedelta(date.today(), birth_date).years
        if age < 14:
            await message.answer("Для регистрации вам должно быть не менее 14 лет. Пожалуйста, проверьте дату:")
            return
        if age > 100:
            await message.answer("Указанный возраст превышает 100 лет. Пожалуйста, проверьте дату:")
            return

        await state.update_data(date_of_birth=date_string)
        user_data = await state.get_data()

        async with async_session_maker() as session:
            phone = user_data.get('phone', None)
            if phone:
                obj = select(UserTelegram).where(UserTelegram.phone == phone)
                result = await session.execute(obj)
                user = result.scalars().first()
                if user:
                    await message.answer("Пользователь с этим номером телефона уже существует!")
                    await state.clear()
                    return

            stmt = insert(UserTelegram).values(
                username=message.from_user.username,
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                middle_name=user_data['middle_name'],
                phone=phone,
                date_of_birth=birth_date,
                user_id=message.from_user.id
            ).returning(UserTelegram)
            await session.execute(stmt)
            await session.commit()

            admins = await session.execute(select(UserTelegram).where(UserTelegram.admin == True))
            for admin in admins.scalars().unique().all():
                try:
                    await message.bot.send_message(admin.user_id, f"Зарегистрировался новый пользователь: {user_data['first_name']} {user_data['middle_name']} (@{user.username})!")
                except Exception as e:
                    print(e)

        await message.answer("Регистрация успешно завершена!")
        await state.clear()

    except ValueError:
        await message.answer("Неверный формат даты. Пожалуйста, используйте формат ГГГГ-ММ-ДД (например, 1990-01-31):")


async def cheek_registration(message: types.Message):
    async with async_session_maker() as session:
        stmt = select(UserTelegram).where(UserTelegram.user_id == message.from_user.id)
        result = await session.execute(stmt)
        user = result.scalars().first()
        return user


def register_handlers_registration(dp: Dispatcher):
    dp.message.register(start_registration, Command(commands=['register']))
    dp.message.register(process_first_name, Registration.first_name)
    dp.message.register(process_last_name, Registration.last_name)
    dp.message.register(process_middle_name, Registration.middle_name)
    dp.message.register(process_phone, Registration.phone)
    dp.message.register(process_date_of_birth, Registration.date_of_birth)
