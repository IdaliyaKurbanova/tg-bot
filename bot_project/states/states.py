"""
Модуль с группами состояний.
"""

from aiogram.fsm.state import StatesGroup, State


class UserState(StatesGroup):
    """
    Класс-группа состояний для создания нового пользователя.
    """

    name = State()


class TicketState(StatesGroup):
    """
    Класс-группа состояний для выбора параметров билета с целью дальнейшего поиска.
    """

    origin_city = State()
    destination_city = State()
    return_ticket = State()
    count_to_show = State()
    change_date = State()
    group_by = State()
