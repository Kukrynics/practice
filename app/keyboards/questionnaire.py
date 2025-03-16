from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
)
import logging

# Кнопка для просмотра всех анкет
view_all_questionnaires = KeyboardButton(text='Все мои анкеты')

# Клавиатура для выбора действия с анкетой
def get_questionnaire_action_keyboard(questionnaire_id: int):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Просмотреть', callback_data=f'view_questionnaire_{questionnaire_id}')],
        [InlineKeyboardButton(text='Редактировать', callback_data=f'edit_questionnaire_{questionnaire_id}')],
        [InlineKeyboardButton(text='Назад', callback_data='back_to_questionnaire_list')]
    ])
    return keyboard

# Создание клавиатуры для выбора анкеты
def get_questionnaires_list_keyboard(questionnaires):
    logger = logging.getLogger(__name__)
    logger.debug(f"Создание клавиатуры для {len(questionnaires)} анкет")
    
    buttons = []
    for i, questionnaire in enumerate(questionnaires):
        job_title = questionnaire.job_opening.title
        date = questionnaire.created_at.strftime('%Y-%m-%d')
        callback_data = f"select_questionnaire_{questionnaire.id}"
        
        logger.debug(f"Создаем кнопку для анкеты {questionnaire.id}")
        logger.debug(f"Текст кнопки: '{job_title} ({date})'")
        logger.debug(f"Callback data: '{callback_data}'")
        
        button = InlineKeyboardButton(
            text=f"{job_title} ({date})",
            callback_data=callback_data
        )
        buttons.append([button])
        logger.debug(f"Кнопка добавлена в клавиатуру")
    
    # Добавляем кнопку "Назад"
    back_button = InlineKeyboardButton(text='Назад', callback_data='back_to_main')
    buttons.append([back_button])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    logger.debug(f"Создана клавиатура с {len(buttons)} кнопками")
    return keyboard

# Создание клавиатуры для выбора вопроса для редактирования
def get_questions_keyboard(questionnaire_data, questionnaire_id):
    buttons = []
    for i, (question, _) in enumerate(questionnaire_data.items()):
        buttons.append([InlineKeyboardButton(
            text=f"{i+1}. {question[:30]}...",
            callback_data=f"edit_question_{questionnaire_id}_{i}"
        )])
    
    # Добавляем кнопку "Назад"
    buttons.append([InlineKeyboardButton(text='Назад', callback_data='back_to_questionnaire_list')])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)
