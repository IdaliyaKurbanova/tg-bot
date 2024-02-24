"""
Модуль с reply-кнопками.
"""

from aiogram.utils.keyboard import ReplyKeyboardBuilder, ReplyKeyboardMarkup


def main_keyboard() -> ReplyKeyboardMarkup:
    """
    Функция создает клавиатуру с основными командами.
    """
    main_kb_builder = ReplyKeyboardBuilder()
    main_kb_builder.button(text="/low")
    main_kb_builder.button(text="/high")
    main_kb_builder.button(text="/custom")
    main_kb_builder.button(text="/history")
    return main_kb_builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
