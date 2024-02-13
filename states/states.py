from aiogram.fsm.state import StatesGroup, State


class UserState(StatesGroup):
    name = State()


class TicketState(StatesGroup):
    origin_city = State()
    destination_city = State()
    return_ticket = State()
    count_to_show = State()
    change_date = State()
    group_by = State()
