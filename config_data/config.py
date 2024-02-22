"""
Данный модуль представляет собой конфигурационный файл, который хранит и получает из переменных окружения (файл .env)
константы, необходимые для работы бота.
"""

import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit("Переменные окружения не загружены, так как отсутствует файл .env")
else:
    load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN")
API_KEY: str = os.getenv("API_KEY")


