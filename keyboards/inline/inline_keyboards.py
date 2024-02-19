from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup
from aiogram_calendar import SimpleCalendar, get_user_locale
from aiogram import types
from datetime import datetime


def site_url_kb(return_date="", **kwargs):
    url_builder = InlineKeyboardBuilder()
    if len(kwargs['departure_at']) > 7:
        departure_list = kwargs['departure_at'][-5:].split("-")
        departure_date = "".join([departure_list[1], departure_list[0]])
    else:
        departure_date = "01" + kwargs['departure_at'][-2:]
    if "return_at" in kwargs.keys():
        return_at = kwargs['return_at']
        if len(return_at) > 7:
            return_list = return_at[-5:].split("-")
            return_date = "".join([return_list[1], return_list[0]])
        else:
            return_date = "01" + return_at[-2:]

    url_builder.button(text="Aviasales",
                       url=f"https://www.aviasales.ru/search/{kwargs['origin']}"
                           f"{departure_date}{kwargs['destination']}{return_date}1")
    return url_builder.as_markup()


def y_n_kb():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.row(InlineKeyboardButton(text="Да", callback_data="Да"))
    kb_builder.row(InlineKeyboardButton(text="Нет", callback_data="Нет"))
    return kb_builder.as_markup()


def group_by_kb():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.row(InlineKeyboardButton(text="Дата отправления", callback_data="departure_at"))
    kb_builder.row(InlineKeyboardButton(text="Дата возвращения", callback_data="return_at"))
    return kb_builder.as_markup()


def date_choice_kb():
    type_kb_builder = InlineKeyboardBuilder()
    type_kb_builder.row(InlineKeyboardButton(text="Точная дата", callback_data="exact_date"))
    type_kb_builder.row(InlineKeyboardButton(text="Только месяц", callback_data="month"))
    return type_kb_builder.as_markup()


async def create_calendar(user: types.User) -> SimpleCalendar:
    calendar_kb = SimpleCalendar(locale=await get_user_locale(user), show_alerts=True)
    date_now = datetime.now()
    calendar_kb.set_dates_range(datetime(date_now.year, 1, 1), datetime(date_now.year + 1, 12, 31))
    return calendar_kb


async def start_calendar_kb(user: types.User) -> InlineKeyboardMarkup:
    date_now = datetime.now()
    return await (await create_calendar(user)).start_calendar(year=date_now.year, month=date_now.month)


def repeat_question_kb():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.row(InlineKeyboardButton(text="Да", callback_data="repeat_request_again"))
    kb_builder.row(InlineKeyboardButton(text="Нет", callback_data="finish_command"))
    return kb_builder.as_markup()


def request_number_kb(list_length: int):
    kb_builder = InlineKeyboardBuilder()
    for num in range(1, list_length + 1):
        kb_builder.row(InlineKeyboardButton(text=f"{num}", callback_data=str(num)))

    return kb_builder.as_markup()

