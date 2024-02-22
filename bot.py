"""
Модуль, в котором инициализируется и запускается бот.
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from config_data import config
from handlers.default_handlers.default_handlers import default_router
from handlers.custom_handlers.low_high_custom import low_router
from handlers.custom_handlers.history import history_router


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(default_router)
    dp.include_routers(low_router)
    dp.include_routers(history_router)
    bot = Bot(token=config.BOT_TOKEN)
    await bot.set_my_commands([BotCommand(command='start', description='Запустить бота'),
                               BotCommand(command='help', description='Помощь'),
                               BotCommand(command='exit', description='Завершить запрос')])
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
