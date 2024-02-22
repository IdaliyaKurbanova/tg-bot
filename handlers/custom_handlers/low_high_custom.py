"""
Модуль с обработчиками и функциями для команд low, high, custom.
"""
from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.handlers.message import Message
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove, CallbackQuery
from typing import List, Optional, Any
from states.states import TicketState
from siteAPI_info import APIResult
from database.utils import CityMethods, HistoryMethods
from keyboards.reply.reply_keyboards import main_keyboard
from keyboards.inline.inline_keyboards import (site_url_kb, create_calendar, start_calendar_kb, group_by_kb,
                                               date_choice_kb, y_n_kb, change_date_kb)
import json
from aiogram_calendar import SimpleCalendarCallback
from datetime import datetime

low_router = Router()

group_by_options: List[str] = ["departure_at", "return_at"]
date_types: List[str] = ['exact_date', 'month']


async def find_api_results(message: Message, state: FSMContext) -> Any:
    """
    Функция, которая импортирует из состояния пользователя параметры поиска, сохраненные в ходе предыдущих шагов,
    и обращаясь к классу APIResult находит по API билеты. Параметры и результаты поиска сохраняются в таблицу histories.
    :return: api_result - результаты поиска по API в виде списка строк или просто строки.
    """
    user_data: dict = await state.get_data()
    if user_data.get('request') == "low":
        api_result: Optional[list, str] = APIResult.get_cheapest_ticket(**user_data)
    elif user_data.get('request') == "custom":
        api_result: Optional[list, str] = APIResult.get_custom_tickets_short(**user_data)
    else:
        api_result: Optional[list, str] = APIResult.get_direct_ticket(**user_data)
    if api_result is None:
        HistoryMethods.create_history(search_params=json.dumps(user_data), search_result=api_result,
                                      user_tg_id=user_data['user_tg_id'])
    else:
        api_result_str: str = ", ".join(api_result)
        HistoryMethods.create_history(search_params=json.dumps(user_data), search_result=api_result_str,
                                      user_tg_id=user_data['user_tg_id'])
    return api_result


async def answer_to_user(message: Message, state: FSMContext, api_result: Optional[Any], default_num: int = 3,
                         not_defined_by_user: bool = True) -> None:
    """
    Функция, которая получает на вход результаты поиска билетов и вывод соответствующий ответ пользователю.
    Если билеты не были найдены, то об этом сообщается пользователю.
    Если список с результатами поиска состоит из более чем 3-х элементов, то пользователю предоставляется возможность выбрать,
    какое количество билетов он хочет просмотреть и предлагается ввести цифру.
    Если элементов в результатах поиска меньше трех или пользователь уже указал, сколько билетов хочет посмотреть,
    то информация по билетам выводится пользователю.
    :param api_result: результат поиска билетов по параметрам пользователя
    :param default_num: количество билетов, которое необходимо вывести для просмотра пользователю.
    :param not_defined_by_user: булеву-значение, которое означает определено ли пользователем желаемое
     количество билетов для просмотра. По умолчанию False.
    :return: None
    """
    user_data: dict = await state.get_data()
    if api_result is None or api_result == [] or api_result == {}:
        if user_data.get("request") == "low":
            await message.answer(text="К сожалению, по вашему запросу результаты не найдены.\n"
                                      "Хотите поменять даты вылета?", reply_markup=change_date_kb())
            await state.set_state(TicketState.change_date)
        elif user_data.get("request") == "high":
            await message.answer(
                text="К сожалению, для данного направления и выбранных дат прямые билеты не найдены. \n"
                     "Попробуйте поменять параметры или сделать запрос позже.")
            await state.clear()
        else:
            await message.answer(text="К сожалению, по вашему запросу результаты не найдены. "
                                      "\nПопробуйте сделать запрос позже")
            await state.clear()
    elif len(api_result) > 3 and not_defined_by_user:
        if user_data.get("request") == "low":
            await message.answer(text=f"По вашему запросу найдено {len(api_result)} вариантов.\n"
                                      f"Какое количество ответов вывести?", reply_markup=ReplyKeyboardRemove())
            await state.update_data(api_result=api_result)
            await state.set_state(TicketState.count_to_show)
        else:
            if user_data.get("return_at", 0) and user_data.get("group_by") == "departure_at":
                text: str = "Туда/   Обратно/  Цена за 2б./   Время туда+обратно\n" + api_result
            elif user_data.get("return_at", 0) and user_data.get("group_by") == "return_at":
                text: str = "Обратно/   Туда/  Цена за 2б./   Время туда+обратно\n" + api_result
            else:
                text: str = "Дата/    Цена/   Общее время в пути\n" + api_result
            await message.answer(text=text)
            await message.answer(text='Для заказа и получения деталей перейдите по ссылке:',
                                 reply_markup=site_url_kb(**user_data))
            await state.clear()
    else:
        if user_data.get("request") in ["low", "high"]:
            if not_defined_by_user is False:
                for ticket in api_result[:default_num]:
                    await message.answer(text=ticket)
            else:
                for ticket in api_result:
                    await message.answer(text=ticket)
        else:
            await message.answer(text=api_result)
        await message.answer(text='Для заказа и получения деталей перейдите по ссылке:',
                             reply_markup=site_url_kb(**user_data))
        await state.clear()


@low_router.message(StateFilter(None), Command("low"))
async def low_command(message: Message, state: FSMContext) -> None:
    """
    Обработчик команды low. Записывает в хранилище состояний название команды и переводит пользователя в
    состояние ввода города отправления.
    """
    await message.answer(text="Для поиска самого дешёвого билета введите город отправления.\n"
                              "Например: Москва", reply_markup=ReplyKeyboardRemove())
    await state.update_data(request="low")
    await state.set_state(TicketState.origin_city)


@low_router.message(StateFilter(None), Command("custom"))
async def custom_command(message: Message, state: FSMContext) -> None:
    """
    Обработчик команды custom. Записывает в хранилище состояний название команды и переводит пользователя в
    состояние ввода города отправления.
    """
    await state.update_data(request="custom")
    await message.answer(text="Для поиска дешёвых билетов за каждый день периода введите город отправления.\n"
                              "Например: Москва", reply_markup=ReplyKeyboardRemove())
    await state.set_state(TicketState.origin_city)


@low_router.message(StateFilter(None), Command("high"))
async def high_command(message: Message, state: FSMContext) -> None:
    """
    Обработчик команды high. Записывает в хранилище состояний название команды и переводит пользователя в
    состояние ввода города отправления.
    """
    await message.answer(text="Для поиска прямого билета введите город отправления.\n"
                              "Например: Москва", reply_markup=ReplyKeyboardRemove())
    await state.update_data(request="high")
    await state.set_state(TicketState.origin_city)


@low_router.message(TicketState.origin_city)
async def get_origin_city(message: Message, state: FSMContext) -> None:
    """
    Функция для обработки сообщений пользователя в состоянии ввода города отправления.
    В случае корректного ввода города (что проверяется запросом в базу данных кода для введенного города)
    код города сохраняется в хранилище и пользователь переводится в состояние ввода города назначения.
    """
    try:
        origin_city: str = message.text.strip().lower()
        origin_code: str = CityMethods.get_city_code(origin_city)
        if origin_code is None:
            await message.answer(text='Ошибка! Некорректно введен город отправления\n'
                                      'Попробуйте снова:')
        else:
            await state.update_data(origin=origin_code)
            await state.update_data(user_tg_id=message.from_user.id)
            await message.answer(text='А теперь введите город назначения:',
                                 reply_markup=ReplyKeyboardRemove())
            await state.set_state(TicketState.destination_city)
    except Exception:
        await message.answer(text='Ошибка! Некорректно введен город.\n'
                                  'Попробуйте снова:')


@low_router.message(TicketState.destination_city)
async def define_cities(message: Message, state: FSMContext) -> None:
    """
    Функция для обработки сообщений пользователя в состоянии ввода города назначения.
    В случае корректного ввода города (что проверяется запросом в базу данных кода для введенного города)
    код города сохраняется в хранилище и пользователь переводится в состояние выбора типа даты
    для отправления (для команд low и high) и выбора даты на клавиатуре (для команды custom).
    """
    user_data: dict = await state.get_data()
    try:
        destination_city: str = message.text.strip().lower()
        destination_code: str = CityMethods.get_city_code(destination_city)
        if destination_code is None:
            await message.answer(text='Ошибка! Некорректно введен город назначения.\n'
                                      'Попробуйте снова:')
        else:
            await state.update_data(destination=destination_code)
            if user_data.get("request") in ["high", "low"]:
                await message.answer(text='Отлично! Перейдем к дате отправления.\n'
                                          'Вы хотите ввести точную дату или указать только месяц?',
                                     reply_markup=date_choice_kb())
            else:
                text: str = 'Отлично! А теперь введите любое число месяца отправления:'
                await message.answer(text=text,
                                     reply_markup=await start_calendar_kb(message.from_user))

    except Exception:
        await message.answer(text='Ошибка! Некорректно введен город назначения.\n'
                                  'Попробуйте снова:')


@low_router.callback_query(SimpleCalendarCallback.filter())
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: SimpleCalendarCallback,
                                  state: FSMContext) -> None:
    """
    Колбэк-функция для обработки клавиатуры выбора даты. Если пользователь успешно выбрал на клавиатуре дату:
    1) если выбрана дата отправления (что определятся по булеву-значению параметра one_way),
    то дата сохраняется в хранилище и у пользователя спрашивают, нужен ли обратный билет и вызываются кнопки "Да" и "Нет".
    2) если выбрана дата возращения, то дата сохраняется в хранилище и для команды custom пользователь переводится
    в состояние выбора метода сортировки результатов, а для команд low и high вызывается функция find_api_result
    для поиска билетов по API.
    """
    calendar = await create_calendar(callback_query.from_user)
    selected, date = await calendar.process_selection(callback_query, callback_data)
    user_data: dict = await state.get_data()
    if selected:
        if user_data.get("one_way", None) is None:
            if user_data.get('date_type') == "exact_date":
                await state.update_data(departure_at=date.strftime("%Y-%m-%d"))
                await callback_query.message.answer(text=f'Вы выбрали {date.strftime("%d/%m/%Y")}.\n')
            else:
                await state.update_data(departure_at=date.strftime("%Y-%m"))
                await callback_query.message.answer(text=f'Вы выбрали месяц {date.strftime("%m.%Y")}.\n')
            await callback_query.message.answer(text=f'Вам нужен обратный билет?\n'
                                                     f'Выберите да или нет...', reply_markup=y_n_kb())
        else:
            if user_data.get("date_type") == "exact_date":
                departure_at_str = user_data.get('departure_at')
                if len(departure_at_str) > 7:
                    departure_at_date = datetime.strptime(departure_at_str, "%Y-%m-%d")
                else:
                    departure_at_date = datetime.strptime(departure_at_str, "%Y-%m")

                if date < departure_at_date:
                    await callback_query.message.answer(text="Дата возвращения не может быть раньше даты вылета туда.\n"
                                                             "Введите дату возвращения снова: ",
                                                        reply_markup=await start_calendar_kb(callback_query.from_user))
                else:
                    await state.update_data(return_at=date.strftime("%Y-%m-%d"))
                    await callback_query.message.answer(text=f'Вы выбрали {date.strftime("%d/%m/%Y")}.\n')
                    api_result = await find_api_results(callback_query.message, state)
                    await answer_to_user(callback_query.message, state, api_result)
            else:
                departure_at_str = user_data.get('departure_at')
                if len(departure_at_str) > 7:
                    departure_at_date = datetime.strptime(departure_at_str, "%Y-%m-%d")
                else:
                    departure_at_date = datetime.strptime(departure_at_str, "%Y-%m")
                if date.month < departure_at_date.month:
                    await callback_query.message.answer(text="Дата возвращения не может быть раньше даты вылета туда.\n"
                                                             "Введите дату возвращения снова: ",
                                                        reply_markup=await start_calendar_kb(
                                                            callback_query.from_user))
                else:
                    await state.update_data(return_at=date.strftime("%Y-%m"))
                    await callback_query.message.answer(
                        text=f'Вы выбрали месяц возвращения {date.strftime("%m.%Y")}.\n')
                    if user_data.get("request") == "custom":
                        await callback_query.message.answer("А теперь выберите признак, "
                                                            "по которому хотите сгруппировать билеты: ",
                                                            reply_markup=group_by_kb())
                        await state.set_state(TicketState.group_by)
                    else:
                        api_result = await find_api_results(callback_query.message, state)
                        await answer_to_user(callback_query.message, state, api_result)


@low_router.callback_query(F.data.in_(["Да", "Нет"]))
async def answer_return_ticket(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Функция для обработки клавиатуры, нужен ли пользователю обратный билет.
    Если пользователь отвечает положительно, то отправляется к выбору типа даты для обратного билета.
    В случае отрицательного ответа, вызывается функция find_api_result, которая ищет билет по параметрам пользователя
    и передает найденный результат в функцию answer_to_user, которая выводит билеты пользователю.
    """
    user_data: dict = await state.get_data()
    if callback.data == "Да":
        await state.update_data(one_way=False)
        if user_data.get("request") in ["low", "high"]:
            await callback.message.answer(text='Вы хотите указать точную дату обратного вылета или только месяц?',
                                          reply_markup=date_choice_kb())
        else:
            await callback.message.answer(text='Введите любое число месяца обратного вылета...',
                                          reply_markup=await start_calendar_kb(callback.from_user))

    else:
        api_result: Optional[list, str] = await find_api_results(callback.message, state)
        await answer_to_user(callback.message, state, api_result)


@low_router.message(TicketState.count_to_show)
async def counts_to_show(message: Message, state: FSMContext) -> None:
    """
    Функция для обработки ввода пользователем количества билетов для просмотра.
    При успешном вводе вызывается функция answer_to_user, которая выводит пользователю выбранное им количество билетов.
    """
    user_data: dict = await state.get_data()
    api_result: Optional[list, str] = user_data.get("api_result")
    try:
        count_to_show = int(message.text.strip())
        if 1 <= count_to_show <= len(api_result):
            await answer_to_user(message, state, api_result, default_num=count_to_show, not_defined_by_user=False)
        else:
            await message.answer(text=f"Ошибка! Введите число в допустимых пределах, максимально - {len(api_result)}")
    except TypeError:
        await message.answer(text=f"Ошибка! Введите корректное число, максимально - {len(api_result)}")


@low_router.callback_query(F.data.in_(["Поменять", "Завершить"]))
async def change_dates(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Функция для обработки ответа пользователя по желанию изменить даты при неуспешном поиске билетов.
    Если пользователь ответил положительно, то пользователь переводится в состояние выбора типа даты.
    Либо запрос завершается.
    """
    if callback.data == "Поменять":
        await state.update_data(one_way=None)
        await callback.message.answer(text='Вы хотите указать точную дату вылета или только месяц?',
                             reply_markup=date_choice_kb())
    else:
        await callback.message.answer(text="Благодарю за обращение. Завершаю обработку запроса...",
                             reply_markup=main_keyboard())
        await state.clear()


@low_router.callback_query(F.data.in_(group_by_options))
async def group_tickets_by(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Колбэк-функция для обработки ответа пользователя на вопрос о признаке для сортировки билетов.
    Признак группировки записывается в хранилище и вызывается функция find_api_results,
    которая осуществляет поиск билетов и найденный результат передает в функцию answer_to_user для показа пользователю.
    """
    action: str = callback.data
    await state.update_data(group_by=action)
    await callback.message.answer(text='Спасибо. Выполняю запрос ...')
    api_result = await find_api_results(callback.message, state)
    await answer_to_user(callback.message, state, api_result)
    await callback.answer()


@low_router.callback_query(F.data.in_(date_types))
async def date_type_choice(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Функция для обработки выбранного пользователем типа даты.
    Выбранный тип даты записывается в хранилище и открывается клавиатура для выбора даты.
    """
    action: str = callback.data
    await state.update_data(date_type=action)
    if action == 'exact_date':
        await callback.message.answer(text="Выберите точную дату:", reply_markup=await start_calendar_kb(
            callback.from_user))
    elif action == 'month':
        await callback.message.answer(text="Выберите любой день месяца вылета", reply_markup=await start_calendar_kb(
            callback.from_user))
