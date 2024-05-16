"""
Модуль с функциями для создания в базе данных таблиц с авиа-кодами городов и авиалиний.
"""

from siteAPI_info import APIResult
from database.models import Airline, City, Session


def necessary_codes_creation() -> None:
    """
    Данная функция путем обращения к методу APIResult из файла siteAPI_info получает по API словарь
    с iata-кодами всех городов и авиалиний и создает в базе данных таблицы airlines и cities с перечислением всех полученных кодов.
    Коды городов и авиалиний необходимы для дальнейшего поиска ботом авиабилетов.

    :return: None
    """
    airline_codes: dict = APIResult.get_airlines_codes()
    cities_codes: dict = APIResult.get_cities_codes()
    with Session() as session:
        list_of_airline_codes = [
            Airline(code=line["code"], name=line["name_translations"]["en"])
            for line in airline_codes
        ]
        list_of_cities_codes = [
            City(code=city["code"], name=str(city["name"]).lower())
            for city in cities_codes
        ]
        session.add_all(list_of_airline_codes)
        session.add_all(list_of_cities_codes)
        session.commit()
