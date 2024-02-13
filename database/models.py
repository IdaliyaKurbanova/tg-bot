from sqlalchemy import create_engine, Column, Integer, Text, String, DateTime, BigInteger, ForeignKey
from sqlalchemy.orm import DeclarativeBase, sessionmaker, relationship
from datetime import datetime

db_engine = create_engine('sqlite:///bot.db', echo=False)
db_engine.connect()
Session = sessionmaker(db_engine)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True)
    name = Column(String)
    histories = relationship("History", back_populates="user")
    registrated_at = Column(DateTime, default=datetime.now())

    def __init__(self, telegram_id, name):
        self.telegram_id = telegram_id
        self.name = name


class Airline(Base):
    __tablename__ = 'airlines'

    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True)
    name = Column(String)


class City(Base):
    __tablename__ = 'cities'

    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True)
    name = Column(String)


class History(Base):
    __tablename__ = 'histories'

    id = Column(Integer, primary_key=True)
    user = relationship("User", back_populates="histories")
    user_tg_id = Column(Integer, ForeignKey("users.telegram_id"))
    created_at = Column(DateTime, default=datetime.now())
    search_params = Column(Text)
    search_result = Column(Text)


def create_db() -> None:
    Base.metadata.create_all(db_engine)