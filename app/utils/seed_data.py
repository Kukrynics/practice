import asyncio
from datetime import datetime
from sqlalchemy import insert

from app.utils.datebase import async_session_maker
from app.models.users import UserTelegram, JobOpenings, Question, Questionnaire


async def seed_data():
    """Наполняет базу данных тестовыми данными"""
    async with async_session_maker() as session:
        # Добавляем пользователей
        users = [
            {
                "user_id": 123456789,
                "username": "test_user1",
                "first_name": "Иван",
                "middle_name": "Иванович",
                "last_name": "Иванов",
                "phone": "+79001234567",
                "date_of_birth": datetime(1990, 1, 1),
                "admin": True
            },
            {
                "user_id": 987654321,
                "username": "test_user2",
                "first_name": "Петр",
                "middle_name": "Петрович",
                "last_name": "Петров",
                "phone": "+79009876543",
                "date_of_birth": datetime(1995, 5, 5),
                "admin": False
            }
        ]
        
        for user_data in users:
            stmt = insert(UserTelegram).values(**user_data)
            await session.execute(stmt)
        
        # Добавляем вакансии
        job_openings = [
            {
                "title": "Python разработчик",
                "description": "Требуется Python разработчик с опытом работы от 2 лет. Знание Django, FastAPI, SQLAlchemy.",
                "user_id_create": 123456789,
                "flag": True
            },
            {
                "title": "Frontend разработчик",
                "description": "Требуется Frontend разработчик с опытом работы от 1 года. Знание React, TypeScript, CSS.",
                "user_id_create": 123456789,
                "flag": True
            },
            {
                "title": "DevOps инженер",
                "description": "Требуется DevOps инженер с опытом работы от 3 лет. Знание Docker, Kubernetes, CI/CD.",
                "user_id_create": 123456789,
                "flag": True
            }
        ]
        
        for job_data in job_openings:
            result = await session.execute(insert(JobOpenings).values(**job_data).returning(JobOpenings.id))
            job_id = result.scalar_one()
            
            # Добавляем вопросы для каждой вакансии
            if job_data["title"] == "Python разработчик":
                questions = [
                    {"text": "Расскажите о своем опыте работы с Python", "job_opening_id": job_id},
                    {"text": "Какие фреймворки Python вы знаете?", "job_opening_id": job_id},
                    {"text": "Расскажите о своем опыте работы с базами данных", "job_opening_id": job_id},
                    {"text": "Какие проекты на Python вы реализовали?", "job_opening_id": job_id}
                ]
            elif job_data["title"] == "Frontend разработчик":
                questions = [
                    {"text": "Расскажите о своем опыте работы с React", "job_opening_id": job_id},
                    {"text": "Какие CSS-фреймворки вы использовали?", "job_opening_id": job_id},
                    {"text": "Расскажите о своем опыте работы с TypeScript", "job_opening_id": job_id},
                    {"text": "Какие проекты на Frontend вы реализовали?", "job_opening_id": job_id}
                ]
            else:
                questions = [
                    {"text": "Расскажите о своем опыте работы с Docker", "job_opening_id": job_id},
                    {"text": "Какие инструменты CI/CD вы использовали?", "job_opening_id": job_id},
                    {"text": "Расскажите о своем опыте работы с Kubernetes", "job_opening_id": job_id},
                    {"text": "Какие проекты по DevOps вы реализовали?", "job_opening_id": job_id}
                ]
            
            for question_data in questions:
                await session.execute(insert(Question).values(**question_data))
        
        # Добавляем анкеты (заполненные опросники)
        questionnaires = [
            {
                "user_id": 987654321,
                "job_opening_id": 1,  # Python разработчик
                "data": {
                    "1": "Имею опыт работы с Python 3 года. Работал в компании X над проектом Y.",
                    "2": "Django, FastAPI, Flask, Pyramid",
                    "3": "Работал с PostgreSQL, MySQL, MongoDB",
                    "4": "Разработал API для системы управления контентом, создал бота для Telegram"
                }
            },
            {
                "user_id": 987654321,
                "job_opening_id": 2,  # Frontend разработчик
                "data": {
                    "1": "Имею опыт работы с React 2 года. Работал в компании Z над проектом W.",
                    "2": "Bootstrap, Tailwind CSS, Material UI",
                    "3": "Использую TypeScript последние 1.5 года во всех проектах",
                    "4": "Разработал интерфейс для системы управления задачами, создал лендинг для продукта"
                }
            }
        ]
        
        for questionnaire_data in questionnaires:
            await session.execute(insert(Questionnaire).values(**questionnaire_data))
        
        await session.commit()
        print("База данных успешно наполнена тестовыми данными!")


if __name__ == "__main__":
    asyncio.run(seed_data())
