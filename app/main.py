import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.bot import DefaultBotProperties
from app.callback.jobs import register_job_openings_handlers
from app.callback.profile import register_profile_handlers
from app.callback.questionnaire import register_questionnaire_handlers
from app.keyboards.start import keyboard_start
from app.utils.config import settings
from aiogram.filters import Command
from app.registration import cheek_registration, register_handlers_registration

# Настраиваем логирование
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Включаем отладочное логирование для aiogram
aiogram_logger = logging.getLogger("aiogram")
aiogram_logger.setLevel(logging.DEBUG)

bot = Bot(token=settings.TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


# Middleware для логирования всех обновлений
@dp.update.outer_middleware()
async def log_updates(handler, event, data):
    logger.debug(f"Получено обновление: {event.model_dump_json(exclude_none=True)}")
    try:
        return await handler(event, data)
    except Exception as e:
        logger.exception(f"Ошибка при обработке обновления: {e}")
        raise


@dp.message(Command(commands=['start']))
async def start(message: types.Message):
    user = await cheek_registration(message)
    if user:
        await message.answer(f"Привет, {user.first_name} {user.middle_name}.\n"
                             "Сейчас я покажу тебе экранную клавиатуру, "
                             "на ней ты сможешь выбрать направление диалога!", reply_markup=keyboard_start)
    else:
        await message.answer("Привет, я бот для прохождения опроса, "
                             "для начала опроса тебе нужно зарегистрироваться.\n"
                             "Для регистрации нажми /register")


async def on_startup():
    logger.info("Бот запущен")

    # Регистрируем специфические обработчики
    register_questionnaire_handlers(dp)  # Регистрируем первым, чтобы он проверялся последним
    register_job_openings_handlers(dp)
    register_profile_handlers(dp)
    register_handlers_registration(dp)
    logger.info("Все специфические обработчики зарегистрированы")

    # Отладочный обработчик для необработанных callback-запросов
    @dp.callback_query()
    async def debug_callback(callback: types.CallbackQuery):
        logger.debug(f"Получен необработанный callback-запрос: {callback.data}")
        await callback.answer()

    logger.info("Отладочный обработчик зарегистрирован")
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(on_startup())
