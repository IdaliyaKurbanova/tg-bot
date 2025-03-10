"""
Модуль, который при запуске создает в базе данных все таблицы.
А также заполняет таблицы airlines и cities необходимыми iata-кодами.
"""

from database.models import create_db
from database.codes_creation import necessary_codes_creation


if __name__ == "__main__":
    create_db()
    necessary_codes_creation()
