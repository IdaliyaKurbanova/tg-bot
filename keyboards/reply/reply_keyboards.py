from aiogram.utils.keyboard import ReplyKeyboardBuilder


def main_keyboard():
    main_kb_builder = ReplyKeyboardBuilder()
    main_kb_builder.button(text="/low")
    main_kb_builder.button(text="/high")
    main_kb_builder.button(text="/custom")
    main_kb_builder.button(text="/history")
    return main_kb_builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def y_n_kb():
    y_n_kb_builder = ReplyKeyboardBuilder()
    y_n_kb_builder.button(text="Да")
    y_n_kb_builder.button(text="Нет")
    return y_n_kb_builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
