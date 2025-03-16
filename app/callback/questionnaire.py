from aiogram import types, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select
import logging

from sqlalchemy.orm.attributes import flag_modified

from app.models.users import Questionnaire, UserTelegram
from app.registration import cheek_registration
from app.utils.datebase import async_session_maker
from app.keyboards.questionnaire import (
    get_questionnaires_list_keyboard,
    get_questionnaire_action_keyboard,
    get_questions_keyboard
)


# Определение состояний для редактирования анкеты
class EditQuestionnaireStates(StatesGroup):
    waiting_for_new_answer = State()


async def show_questionnaire(message: types.Message):
    if message.text == 'Последняя анкета':
        user = await cheek_registration(message)
        if user:
            if user.questionnaires:
                # Получаем последнюю анкету пользователя
                latest_questionnaire = user.questionnaires[0]  # Предполагаем, что анкеты отсортированы по времени

                # Формируем строку с ответами на вопросы
                answers_str = ""
                for question, answer in latest_questionnaire.data.items():
                    answers_str += f"\n- {question}: {answer}"

                await message.answer(f"Ваша Анкета:\n"
                                     f"Имя: {user.first_name}\n"
                                     f"Фамилия: {user.last_name}\n"
                                     f"Отчество: {user.middle_name}\n"
                                     f"Телефон: {user.phone}\n"
                                     f"Дата рождения: {user.date_of_birth.strftime('%Y-%m-%d')}\n"
                                     f"Вакансия: {latest_questionnaire.job_opening.title}\n"
                                     f"Ответы на вопросы: {answers_str}")
            else:
                await message.answer("Анкета не найдена. Пожалуйста, пройдите анкетирование.")
        else:
            await message.answer("Профиль не найден. Пожалуйста, зарегистрируйтесь.")


async def show_all_questionnaires(message: types.Message):
    """Показать список всех анкет пользователя"""
    if message.text == 'Все мои анкеты':
        user = await cheek_registration(message)
        if user:
            if user.questionnaires:
                keyboard = get_questionnaires_list_keyboard(user.questionnaires)
                await message.answer("Выберите анкету для просмотра или редактирования:", reply_markup=keyboard)
            else:
                await message.answer("У вас пока нет заполненных анкет. Пожалуйста, пройдите анкетирование.")
        else:
            await message.answer("Профиль не найден. Пожалуйста, зарегистрируйтесь.")


async def select_questionnaire_callback(callback: types.CallbackQuery):
    logger = logging.getLogger(__name__)
    logger.debug(f"Вызван select_questionnaire_callback")
    logger.debug(f"Callback data: {callback.data}")
    logger.debug(f"Callback message: {callback.message}")
    logger.debug(f"Callback from user: {callback.from_user}")

    try:
        # Извлекаем ID анкеты из callback.data
        questionnaire_id = int(callback.data.split('_')[-1])
        logger.debug(f"ID анкеты: {questionnaire_id}")

        # Получаем анкету из базы данных
        async with async_session_maker() as session:
            query = select(Questionnaire).where(Questionnaire.id == questionnaire_id)
            logger.debug(f"SQL запрос: {query}")

            result = await session.execute(query)
            questionnaire = result.scalar_one_or_none()
            logger.debug(f"Получена анкета: {questionnaire}")

            if not questionnaire:
                logger.error(f"Анкета с ID {questionnaire_id} не найдена")
                await callback.answer("Анкета не найдена", show_alert=True)
                return

            # Создаем клавиатуру для действий с анкетой
            keyboard = types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        types.InlineKeyboardButton(
                            text="Просмотреть",
                            callback_data=f"view_questionnaire_{questionnaire_id}"
                        ),
                        types.InlineKeyboardButton(
                            text="Редактировать",
                            callback_data=f"edit_questionnaire_{questionnaire_id}"
                        )
                    ],
                    [types.InlineKeyboardButton(
                        text="Назад",
                        callback_data="back_to_questionnaire_list"
                    )]
                ]
            )
            logger.debug(f"Создана клавиатура для действий")

            # Отправляем сообщение с действиями
            await callback.message.edit_text(
                f"Выбрана анкета на вакансию: {questionnaire.job_opening.title}\n"
                f"Создана: {questionnaire.created_at.strftime('%Y-%m-%d')}\n"
                "Выберите действие:",
                reply_markup=keyboard
            )
            logger.debug("Отправлено сообщение с действиями")

    except Exception as e:
        logger.exception("Ошибка при обработке callback-запроса")
        await callback.answer("Произошла ошибка при обработке запроса", show_alert=True)

    finally:
        await callback.answer()
        logger.debug("Callback обработан успешно")


async def view_questionnaire_callback(callback: types.CallbackQuery):
    """Просмотр выбранной анкеты"""
    questionnaire_id = int(callback.data.split('_')[-1])

    async with async_session_maker() as session:
        result = await session.execute(select(Questionnaire).where(Questionnaire.id == questionnaire_id))
        questionnaire = result.scalar_one_or_none()

        if questionnaire:
            # Формируем строку с ответами на вопросы
            answers_str = ""
            for question, answer in questionnaire.data.items():
                answers_str += f"\n- {question}: {answer}"

            keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text='Назад', callback_data='back_to_questionnaire_list')]
            ])

            await callback.message.edit_text(
                f"Анкета на вакансию: {questionnaire.job_opening.title}\n"
                f"Дата создания: {questionnaire.created_at.strftime('%Y-%m-%d')}\n"
                f"Ответы на вопросы: {answers_str}",
                reply_markup=keyboard
            )
        else:
            await callback.message.edit_text("Анкета не найдена.")

    await callback.answer()


async def edit_questionnaire_callback(callback: types.CallbackQuery):
    """Редактирование выбранной анкеты"""
    questionnaire_id = int(callback.data.split('_')[-1])

    async with async_session_maker() as session:
        result = await session.execute(select(Questionnaire).where(Questionnaire.id == questionnaire_id))
        questionnaire = result.scalar_one_or_none()

        if questionnaire:
            keyboard = get_questions_keyboard(questionnaire.data, questionnaire_id)
            await callback.message.edit_text(
                "Выберите вопрос для редактирования:",
                reply_markup=keyboard
            )
        else:
            await callback.message.edit_text("Анкета не найдена.")

    await callback.answer()


async def edit_question_callback(callback: types.CallbackQuery, state: FSMContext):
    """Обработка выбора вопроса для редактирования"""
    # Получаем ID анкеты и индекс вопроса
    parts = callback.data.split('_')
    questionnaire_id = int(parts[-2])
    question_index = int(parts[-1])

    async with async_session_maker() as session:
        result = await session.execute(select(Questionnaire).where(Questionnaire.id == questionnaire_id))
        questionnaire = result.scalar_one_or_none()

        if questionnaire:
            # Получаем вопрос по индексу
            questions = list(questionnaire.data.keys())
            if question_index < len(questions):
                question = questions[question_index]
                current_answer = questionnaire.data[question]

                # Сохраняем данные в состоянии
                await state.update_data(
                    questionnaire_id=questionnaire_id,
                    question=question,
                    question_index=question_index
                )

                # Переходим в состояние ожидания нового ответа
                await state.set_state(EditQuestionnaireStates.waiting_for_new_answer)

                await callback.message.edit_text(
                    f"Вопрос: {question}\n\n"
                    f"Текущий ответ: {current_answer}\n\n"
                    f"Введите новый ответ:"
                )
            else:
                await callback.message.edit_text("Вопрос не найден.")
        else:
            await callback.message.edit_text("Анкета не найдена.")

    await callback.answer()


async def process_new_answer(message: types.Message, state: FSMContext):
    """Обработка нового ответа на вопрос"""
    # Получаем данные из состояния
    data = await state.get_data()
    questionnaire_id = data.get('questionnaire_id')
    question = data.get('question')

    # Получаем новый ответ
    new_answer = message.text

    async with async_session_maker() as session:
        result = await session.execute(select(Questionnaire).where(Questionnaire.id == questionnaire_id))
        questionnaire = result.scalar_one_or_none()

        if questionnaire:
            # Обновляем ответ в данных анкеты
            questionnaire_data = questionnaire.data
            old_questionnaire_data = questionnaire_data[question]
            questionnaire_data[question] = new_answer

            # Сохраняем обновленные данные
            questionnaire.data = questionnaire_data
            flag_modified(questionnaire, 'data')
            await session.commit()

            admins = await session.execute(select(UserTelegram).where(UserTelegram.admin == True))
            user_obj = await session.execute(select(UserTelegram).where(UserTelegram.user_id == questionnaire.user_id))
            user = user_obj.scalar()
            for admin in admins.scalars().unique().all():
                try:
                    await message.bot.send_message(admin.user_id,
                                                   f"Пользователь {user.first_name} {user.middle_name} {user.last_name} (@{user.username}) изменил ответ на вопрос в анкете!\n"
                                                   f"Анкета на вакансию: {questionnaire.job_opening.title}\n"
                                                   f"Вопрос: {question}\n"
                                                   f"Старый ответ: {old_questionnaire_data}\n"
                                                   f"Новый ответ: {new_answer}")
                except Exception as e:
                    print(e)

            # Возвращаемся к списку вопросов
            keyboard = get_questions_keyboard(questionnaire.data, questionnaire_id)
            await message.answer(
                f"Ответ успешно обновлен!\n\n"
                f"Выберите другой вопрос для редактирования или нажмите 'Назад':",
                reply_markup=keyboard
            )
        else:
            await message.answer("Анкета не найдена.")

    # Сбрасываем состояние
    await state.clear()


async def back_to_questionnaire_list(callback: types.CallbackQuery):
    """Возврат к списку анкет"""
    user = await cheek_registration(callback.message)
    if user and user.questionnaires:
        keyboard = get_questionnaires_list_keyboard(user.questionnaires)
        await callback.message.edit_text("Выберите анкету для просмотра или редактирования:", reply_markup=keyboard)
    else:
        await callback.message.edit_text("У вас пока нет заполненных анкет.")

    await callback.answer()


async def back_to_main(callback: types.CallbackQuery):
    """Возврат в главное меню"""
    await callback.message.delete()
    await callback.message.answer("Вы вернулись в главное меню.")
    await callback.answer()


def register_questionnaire_handlers(dp: Dispatcher):
    logger = logging.getLogger(__name__)
    logger.info("Начинаем регистрацию обработчиков анкет")

    # Регистрация обработчиков сообщений
    dp.message.register(show_questionnaire, lambda message: message.text == 'Последняя анкета')
    dp.message.register(show_all_questionnaires, lambda message: message.text == 'Все мои анкеты')
    dp.message.register(process_new_answer, EditQuestionnaireStates.waiting_for_new_answer)
    logger.debug("Зарегистрированы обработчики сообщений")

    # Регистрация обработчиков callback-запросов
    # Сначала регистрируем обработчик выбора анкеты из списка
    def select_questionnaire_filter(c: types.CallbackQuery) -> bool:
        logger.debug(f"Проверка callback в фильтре: {c.data}")
        result = isinstance(c.data, str) and c.data.startswith('select_questionnaire_')
        logger.debug(f"Результат проверки фильтра select_questionnaire: {result}")
        return result

    dp.callback_query.register(
        select_questionnaire_callback,
        select_questionnaire_filter
    )
    logger.debug("Зарегистрирован обработчик select_questionnaire_callback")

    # Затем регистрируем обработчики действий с выбранной анкетой
    def view_questionnaire_filter(c: types.CallbackQuery) -> bool:
        logger.debug(f"Проверка callback в фильтре view: {c.data}")
        result = isinstance(c.data, str) and c.data.startswith('view_questionnaire_')
        logger.debug(f"Результат проверки view: {result}")
        return result

    def edit_questionnaire_filter(c: types.CallbackQuery) -> bool:
        logger.debug(f"Проверка callback в фильтре edit: {c.data}")
        result = isinstance(c.data, str) and c.data.startswith('edit_questionnaire_')
        logger.debug(f"Результат проверки edit: {result}")
        return result

    def edit_question_filter(c: types.CallbackQuery) -> bool:
        logger.debug(f"Проверка callback в фильтре edit_question: {c.data}")
        result = isinstance(c.data, str) and c.data.startswith('edit_question_')
        logger.debug(f"Результат проверки edit_question: {result}")
        return result

    dp.callback_query.register(
        view_questionnaire_callback,
        view_questionnaire_filter
    )
    dp.callback_query.register(
        edit_questionnaire_callback,
        edit_questionnaire_filter
    )
    dp.callback_query.register(
        edit_question_callback,
        edit_question_filter
    )
    logger.debug("Зарегистрированы обработчики действий с анкетой")

    # В конце регистрируем обработчики навигации
    def back_to_list_filter(c: types.CallbackQuery) -> bool:
        logger.debug(f"Проверка callback в фильтре back_to_list: {c.data}")
        result = isinstance(c.data, str) and c.data.startswith('back_to_questionnaire_list')
        logger.debug(f"Результат проверки фильтра back_to_list: {result}")
        return result

    def back_to_main_filter(c: types.CallbackQuery) -> bool:
        logger.debug(f"Проверка callback в фильтре back_to_main: {c.data}")
        result = isinstance(c.data, str) and c.data.startswith('back_to_main')
        logger.debug(f"Результат проверки фильтра back_to_main: {result}")
        return result

    dp.callback_query.register(
        back_to_questionnaire_list,
        back_to_list_filter
    )
    dp.callback_query.register(
        back_to_main,
        back_to_main_filter
    )
    logger.debug("Зарегистрированы обработчики навигации")

    logger.info("Регистрация обработчиков анкет завершена")
