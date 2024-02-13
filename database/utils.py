from sqlalchemy import select
from database.models import User, City, Airline, db_engine, History
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(db_engine)


class UserMethods:

    @staticmethod
    def get_user(user_id):
        with Session() as session:
            user_query = select(User).where(User.telegram_id == user_id)
            user = session.execute(user_query).first()
            return user

    @staticmethod
    def registrate_user(user_id: int, username: str):
        with Session() as session:
            new_user = User(telegram_id=user_id, name=username)
            session.add(new_user)
            session.commit()


class AirlineMethods:

    @staticmethod
    def get_airline_name(airline_code):
        with Session() as session:
            airline_name = session.query(Airline).filter(Airline.code == airline_code).first()
            return airline_name.name


class CityMethods:

    @staticmethod
    def get_city_code(city_name):
        with Session() as session:
            city_code = session.query(City).filter(City.name == city_name).first()
            return city_code.code


class HistoryMethods:

    @staticmethod
    def create_history(search_params, search_result, user_tg_id):
        with Session() as session:
            new_history = History(user_tg_id=user_tg_id, search_params=search_params,
                                  search_result=search_result)
            session.add(new_history)
            session.commit()




