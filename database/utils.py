from sqlalchemy import select, desc
from typing import List, Any
from database.models import User, City, Airline, db_engine, History
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(db_engine)


class UserMethods:
    """
    Класс с методами для осуществления запросов в базу данных по таблице users
    """

    @staticmethod
    def get_user(user_id: int) -> List[Any] | None:
        """
        Метод для получения объекта пользователя из таблицы users по его телеграм-id
        :param user_id: телеграм-id пользователя, полученный из сообщения пользователя
        :return: объект пользователя
        """
        with Session() as session:
            user_query = select(User).where(User.telegram_id == user_id)
            user = session.execute(user_query).first()
            return user

    @staticmethod
    def registrate_user(user_id: int, username: str) -> None:
        """
        Метод для создания в таблице users нового пользователя.
        :param user_id: телеграм-id пользователя, полученное из его сообщения
        :param username: имя пользователя, полученное из его сообщения
        :return:
        """
        with Session() as session:
            new_user = User(telegram_id=user_id, name=username)
            session.add(new_user)
            session.commit()


class AirlineMethods:
    """
    Класс с методами для осуществления запросов в базу данных по таблице airlines
    """

    @staticmethod
    def get_airline_name(airline_code: str) -> str:
        """
        Метод для получения названия авиакомпании по её коду.
        :param airline_code: код авиакомпании, название которой необходимо получить
        :return: название авиакомпании
        """
        with Session() as session:
            airline_name = (
                session.query(Airline).filter(Airline.code == airline_code).first()
            )
            return airline_name.name


class CityMethods:
    """
    Класс с методами для осуществления запросов в базу данных по таблице cities
    """

    @staticmethod
    def get_city_code(city_name) -> str:
        """
        Метод для получения кода города по его названию
        :param city_name: название города на русском языке, код которого необходимо получить
        :return: код города
        """
        with Session() as session:
            city = session.query(City).filter(City.name == city_name).first()
            return city.code

    @staticmethod
    def get_city_name(city_code) -> str:
        """
        Метод для получения названия города по его коду
        :param city_code: код города, название которого необходимо получить
        :return: название города
        """
        with Session() as session:
            city = session.query(City).filter(City.code == city_code).first()
            return city.name


class HistoryMethods:
    """
    Класс с методами для осуществления запросов в базу данных по таблице histories
    """

    @staticmethod
    def create_history(search_params, search_result, user_tg_id) -> None:
        """
        Метод для создания в таблице histories новой истории поиска
        :param user_tg_id: телеграм-id пользователя, историю поиска которого необходимо записать в базу данных
               search_params: параметры поиска, указанные пользователем
               search_result: результаты поиска, полученные пользователем
        :return: None
        """
        with Session() as session:
            new_history = History(
                user_tg_id=user_tg_id,
                search_params=search_params,
                search_result=search_result,
            )
            session.add(new_history)
            session.commit()

    @staticmethod
    def get_user_history(user_tg_id) -> List | None:
        """
        Метод для получения из таблицы histories истории запросов пользователя
        :param user_tg_id: телеграм-id пользователя, историю запросов которого необходимо получить.
        :return: 5 последних запросов пользователя
        """
        with Session() as session:
            user_history = (
                session.query(History)
                .filter(History.user_tg_id == user_tg_id)
                .order_by(desc(History.created_at))
                .limit(5)
            )
            return user_history
