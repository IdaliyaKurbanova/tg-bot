"""
Модуль с обработчиком и функциями для команды History.
Данная команда выводит пользователю параметры его 5-ти последних запросов и дает возможность повторить какой-либо
из перечисленных запросов.
"""

from aiogram import F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.handlers.message import Message
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from database.utils import CityMethods, HistoryMethods
from keyboards.reply.reply_keyboards import main_keyboard
from keyboards.inline.inline_keyboards import repeat_question_kb, request_number_kb
from handlers.custom_handlers.low_high_custom import find_api_results, answer_to_user
import json

history_router = Router()
requests_description = {
    "low": "Самый дешёвый билет",
    "high": "Прямой и дешёвый билет",
    "custom": "Дешёвый билет за каждый день",
}


@history_router.message(StateFilter(None), Command("history"))
async def history_command(message: Message, state: FSMContext):
    """
    Функция-обработчик для команды history. Получает из базы данных 5 последних запросов пользователя и выводит
    параметры каждого запроса отдельным сообщением. После предлагает повторить какой-либо из запросов
    и выводит соответствующую кнопку для ответа.
    При отсутствии у пользователя истории поиска, отвечает пользователю соответствующим сообщением.

    :param message: сообщение пользователя, которое принимает обработчик.
    :param state: состояние пользователя, в котором он сейчас находится.
    :return: None
    """
    user_history: list | None = HistoryMethods.get_user_history(message.from_user.id)
    params_list: list = []

    if user_history.first() is not None:
        await message.answer(text="Вот какие последние запросы я нашёл:  \n")
        for index, value in enumerate(user_history):
            params_dict: dict = json.loads(value.search_params)
            params_list.append(params_dict)
            origin_city: str = CityMethods.get_city_name(
                params_dict["origin"]
            ).capitalize()
            destination_city: str = CityMethods.get_city_name(
                params_dict["destination"]
            ).capitalize()
            if "return_at" in params_dict.keys():
                text = f"{index + 1}. {requests_description[params_dict['request']]}\n    {origin_city} - {destination_city}\n    Туда: {params_dict['departure_at']}\n    Обратно: {params_dict['return_at']}\n"
            else:
                text = f"{index + 1}. {requests_description[params_dict['request']]}\n    {origin_city} - {destination_city}\n    Дата вылета: {params_dict['departure_at']}\n"

            await state.update_data(params_list=params_list)
            await message.answer(text)
        await message.answer(
            text="Хотите повторить запрос из истории поиска?",
            reply_markup=repeat_question_kb(),
        )
    else:
        await message.answer(
            text="К сожалению, я не нашел у вас истории запросов. \n"
            "Если хотите, мы можем поискать билеты. Для этого выберите одну из команд ниже:",
            reply_markup=main_keyboard(),
        )


@history_router.callback_query(F.data.in_(["repeat_request_again", "finish_command"]))
async def date_type_choice(callback: CallbackQuery, state: FSMContext):
    """
    Колбэк-функция для обработки ответа пользователя на сообщение о желании повторить какой-либо запрос из истории поиска.
    Если пользователь ответил "Да":
      - если в истории найдено более 1 запроса, функция предлагает пользователю выбрать, какой запрос он хочет повторить.
      - если в истории пользователя только 1 запрос, то вызывается функция find_api_result из модуля low_high_custom,
      которая находит билеты согласно передаваемым в нее параметрам (сохранены в состоянии на предыдущем этапе)
      и полученный результат передается в функцию answer_to_user, которая выводит полученный результат пользователю.
    Если пользователь ответил "Нет", то текущая команда history завершается.
    """

    answer: str = callback.data
    params_data: dict = await state.get_data()
    if answer == "repeat_request_again":
        if len(params_data["params_list"]) == 1:
            await callback.message.answer(text="Выполняю запрос...")
            await state.set_data({})
            await state.update_data(params_data["params_list"][0])
            api_result: str | list = await find_api_results(callback.message, state)
            await answer_to_user(callback.message, state, api_result)
        else:
            await callback.message.answer(
                text="Выберите номер запроса, который хотите выполнить: ",
                reply_markup=request_number_kb(len(params_data["params_list"])),
            )
    elif answer == "finish_command":
        await callback.message.answer(
            text="Спасибо за обращение, завершаю текущий запрос...",
            reply_markup=main_keyboard(),
        )
        await state.clear()


@history_router.callback_query(F.data.in_(["1", "2", "3", "4", "5"]))
async def query_number_choice(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Колбэк - функция, которая получает из ответа пользователя номер запроса для повторного поиска и его параметры.
    Далее вызывает функцию find_api_result, которая находит балеты по API, и отправляет результат в функцию answer_to_user,
    которая выводит ответ пользователю.
    :return:
    """
    req_num: int = int(callback.data)
    params_data: dict = await state.get_data()
    await state.set_data({})
    await state.update_data(params_data["params_list"][req_num - 1])
    await callback.message.answer(text="Спасибо, выполняю...")
    api_result = await find_api_results(callback.message, state)
    await answer_to_user(callback.message, state, api_result)


@history_router.message(StateFilter(None))
async def any_text(message: Message) -> None:
    """
    Функция, которая на любое простое сообщение пользователя (если это не команда и
    если он не находится в скаком-либо состоянии) предлагает выбрать одну из существующих команд.
    """
    await message.answer(
        text="Выберите одну из следующих команд:", reply_markup=main_keyboard()
    )
