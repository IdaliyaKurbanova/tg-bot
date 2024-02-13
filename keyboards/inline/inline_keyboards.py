from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup
from aiogram_calendar import SimpleCalendar, get_user_locale
from aiogram import types
from datetime import datetime


def site_url_kb():
    url_builder = InlineKeyboardBuilder()
    url_builder.button(text="Aviasales", url="https://www.aviasales.ru/")
    return url_builder.as_markup()


def group_by_kb():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.row(InlineKeyboardButton(text="Дата отправления", callback_data="departure_at"))
    kb_builder.row(InlineKeyboardButton(text="Дата возвращения", callback_data="return_at"))
    kb_builder.row(InlineKeyboardButton(text="По месяцам", callback_data="month"))
    return kb_builder.as_markup()


async def create_calendar(user: types.User) -> SimpleCalendar:
    calendar_kb = SimpleCalendar(locale=await get_user_locale(user), show_alerts=True)
    date_now = datetime.now()
    calendar_kb.set_dates_range(datetime(date_now.year, 1, 1), datetime(date_now.year + 1, 12, 31))
    return calendar_kb


async def start_calendar_kb(user: types.User) -> InlineKeyboardMarkup:
    date_now = datetime.now()
    return await (await create_calendar(user)).start_calendar(year=date_now.year, month=date_now.month)
