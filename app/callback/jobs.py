from aiogram import types, Dispatcher
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, insert
from aiogram.fsm.state import State, StatesGroup
from app.keyboards.jobs import generate_jobs_keyboard, generate_job_keyboard_for_questionnaire, \
    keyboard_start_questionnaire
from app.models.users import JobOpenings, Question, Questionnaire, UserTelegram
from app.registration import cheek_registration
from app.utils.datebase import async_session_maker
from aiogram.filters import StateFilter


class QuestionnaireStates(StatesGroup):
    data = State()


async def show_job_openings(message: types.Message):
    if message.text == 'Вакансии':
        user = await cheek_registration(message)
        if user:
            async with async_session_maker() as session:
                stmt = select(JobOpenings).where(JobOpenings.flag)
                obj = await session.execute(stmt)
                job_openings = obj.scalars().all()
                if job_openings:
                    text = 'Доступные вакансии:\n'
                    await message.answer(text, reply_markup=await generate_jobs_keyboard(job_openings))
                else:
                    await message.answer("Вакансии не найдены.")

        else:
            await message.answer("Профиль не найден. Пожалуйста, зарегистрируйтесь.")


async def jobs_callback(callback_query: types.CallbackQuery):
    if callback_query.data.startswith('job_'):
        job_id = int(callback_query.data.split('_')[1])
        async with async_session_maker() as session:
            stmt = select(JobOpenings).where(JobOpenings.id == job_id)
            obj = await session.execute(stmt)
            job_opening = obj.scalars().first()
            if job_opening:
                text = f"Вакансия: {job_opening.title}\n\n{job_opening.description}"
                await callback_query.message.answer(text, reply_markup=await generate_job_keyboard_for_questionnaire(
                    job_opening))
            else:
                await callback_query.message.answer("Вакансия не найдена.")


async def job_callback(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data.startswith('questionnaire_job_'):
        job_id = int(callback_query.data.split('_')[2])
        async with async_session_maker() as session:
            stmt = select(Question).where(Question.job_opening_id == job_id)
            obj = await session.execute(stmt)
            questions = obj.scalars().all()
            if questions:
                questions_str = '\n'.join([f"{index + 1}. {question.text}" for index, question in enumerate(questions)])
                base_str = "\n\nКогда будите готовы, нажмите на кнопку 'Начать анкетирование'."
                await callback_query.message.answer(
                    "Вопросы для анкетирования:\n" + questions_str + base_str,
                    reply_markup=keyboard_start_questionnaire
                )
                await state.update_data(questions=questions, current_question_index=0, job_id=job_id)
                await state.set_state(QuestionnaireStates.data)


async def start_questionnaire(callback_query: types.CallbackQuery, state: FSMContext):
    print(f"start_questionnaire вызвана с callback_data: {callback_query.data}")
    if callback_query.data == 'start_questionnaire_1':
        print("Условие выполнено, начинаем анкетирование")
        data = await state.get_data()
        questions = data.get('questions', [])
        if questions:
            print(f"Найдено {len(questions)} вопросов")
            await callback_query.message.answer(f"Вопрос 1: {questions[0].text}")
            await state.update_data(current_question_index=1, answers={})
        else:
            print("Вопросы не найдены")
            await callback_query.message.answer("Ошибка: вопросы не найдены.")


async def ask_question(message: types.Message, state: FSMContext):
    data = await state.get_data()
    questions = data.get('questions', [])
    index = data.get('current_question_index', 0)
    answers = data.get('answers', {})
    job_id = data.get('job_id', None)
    
    # Сохраняем ответ на предыдущий вопрос
    if index > 0 and index <= len(questions):
        prev_question = questions[index-1]
        answers[prev_question.text] = message.text
        await state.update_data(answers=answers)
    
    # Задаем следующий вопрос
    if index < len(questions):
        await message.answer(f"Вопрос {index+1}: {questions[index].text}")
        await state.update_data(current_question_index=index + 1)
    else:
        # Все вопросы заданы
        await message.answer("Все вопросы заданы. Спасибо за ваши ответы!")
        data_s = await state.get_data()
        answers = data_s.get('answers', {})
        job_id = data_s.get('job_id')
        
        # Сохраняем анкету в базу данных
        try:
            user = await cheek_registration(message)
            if user and job_id:
                async with async_session_maker() as session:
                    # Создаем новую анкету
                    new_questionnaire = Questionnaire(
                        user_id=user.user_id,
                        job_opening_id=job_id,
                        data=answers
                    )
                    session.add(new_questionnaire)
                    await session.commit()
                    await message.answer("Ваша анкета успешно сохранена в базе данных!")
                    admins = await session.execute(select(UserTelegram).where(UserTelegram.admin == True))
                    for admin in admins.scalars().unique().all():
                        try:
                            await message.bot.send_message(admin.user_id,
                                                           f"Пользователь {user.first_name} {user.middle_name} {user.last_name} (@{user.username}) создал новую анкету!\n"
                                                           f"Вакансия: {new_questionnaire.job_opening.title}"
                                                           f"Анкета: {new_questionnaire.data}")
                        except Exception as e:
                            print(e)
            else:
                await message.answer("Не удалось сохранить анкету: пользователь не зарегистрирован или не выбрана вакансия.")
        except Exception as e:
            print(f"Ошибка при сохранении анкеты: {e}")
            await message.answer("Произошла ошибка при сохранении анкеты. Пожалуйста, попробуйте позже.")
        
        # Очищаем состояние
        await state.clear()


def register_job_openings_handlers(dp: Dispatcher):
    dp.message.register(show_job_openings, lambda message: message.text == 'Вакансии')
    dp.callback_query.register(job_callback, lambda c: c.data.startswith('questionnaire_job_'))
    dp.callback_query.register(start_questionnaire, lambda c: c.data == 'start_questionnaire_1')
    dp.callback_query.register(jobs_callback)
    dp.message.register(ask_question, StateFilter(QuestionnaireStates.data))