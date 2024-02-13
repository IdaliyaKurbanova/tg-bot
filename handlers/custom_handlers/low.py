# Добавить кнопки
from aiogram import F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.handlers.message import Message
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove, CallbackQuery

from states.states import TicketState
from siteAPI_info import APIResult
from database.utils import CityMethods, HistoryMethods
from keyboards.reply.reply_keyboards import y_n_kb, main_keyboard
from keyboards.inline.inline_keyboards import site_url_kb, create_calendar, start_calendar_kb, group_by_kb
import json
from aiogram_calendar import SimpleCalendarCallback

low_router = Router()


async def find_api_results(message: Message, state: FSMContext):
    user_data = await state.get_data()
    if user_data.get('request') == "low":
        api_result = APIResult.get_cheapest_ticket(**user_data)
    elif user_data.get('request') == "high":
        api_result = APIResult.get_month_ticket(**user_data)
    else:
        print("дошли до поиска результата")
        api_result = APIResult.get_cheapest_ticket(**user_data)
    if api_result is None:
        HistoryMethods.create_history(search_params=json.dumps(user_data), search_result=api_result,
                                      user_tg_id=message.from_user.id)
    else:
        api_result_str = ", ".join(api_result)
        HistoryMethods.create_history(search_params=json.dumps(user_data), search_result=api_result_str,
                                      user_tg_id=message.from_user.id)
    return api_result


async def answer_to_user(message: Message, state: FSMContext, api_result, default_num=3, not_defined_by_user=True):
    user_data = await state.get_data()
    if api_result is None or api_result == []:
        if user_data.get("request") == "low":
            await message.answer(text="К сожалению, по вашему запросу результаты не найдены.\n"
                                      "Хотите поменять даты вылета?", reply_markup=y_n_kb())
            await state.set_state(TicketState.change_date)
        else:
            await message.answer(text="К сожалению, по вашему запросу результаты не найдены. "
                                      "\nПопробуйте сделать запрос позже")
            await state.clear()
    elif len(api_result) > 3 and not_defined_by_user:
        await message.answer(text=f"По вашему запросу найдено {len(api_result)} вариантов.\n"
                                  f"Какое количество ответов вывести?", reply_markup=ReplyKeyboardRemove())
        await state.update_data(api_result=api_result)
        await state.set_state(TicketState.count_to_show)
    else:
        for ticket in api_result[:default_num]:
            await message.answer(text=ticket)
        await message.answer(text='Для заказа и получения деталей перейдите по ссылке:', reply_markup=site_url_kb())
        await state.clear()


@low_router.message(StateFilter(None), Command("low"))
async def low_command(message: Message, state: FSMContext):
    await message.answer(text="Для поиска самого дешёвого билета введите город отправления.\n"
                              "Например: Москва", reply_markup=ReplyKeyboardRemove())
    await state.update_data(request="low")
    await state.set_state(TicketState.origin_city)


@low_router.message(StateFilter(None), Command("high"))
async def high_command(message: Message, state: FSMContext):
    await state.update_data(request="high")
    await message.answer(text="Для поиска билетов за весь месяц введите город отправления.\n"
                              "Например: Москва", reply_markup=ReplyKeyboardRemove())
    await state.set_state(TicketState.origin_city)


@low_router.message(StateFilter(None), Command("custom"))
async def custom_command(message: Message, state: FSMContext):
    await state.update_data(request="custom")
    await message.answer(text="Для поиска сгруппированных дёшевых билетов введите город отправления.\n"
                              "Например: Москва", reply_markup=ReplyKeyboardRemove())
    await state.set_state(TicketState.origin_city)


@low_router.message(TicketState.origin_city)
async def get_origin_city(message: Message, state: FSMContext):
    try:
        origin_city = message.text.strip().lower()
        origin_code = CityMethods.get_city_code(origin_city)
        if origin_code is None:
            await message.answer(text='Ошибка! Некорректно введен город отправления\n'
                                      'Попробуйте снова:')
        else:
            await state.update_data(origin=origin_code)
            await message.answer(text='А теперь введите город назначения:',
                                 reply_markup=ReplyKeyboardRemove())
            await state.set_state(TicketState.destination_city)
    except Exception:
        await message.answer(text='Ошибка! Некорректно введен город.\n'
                                  'Попробуйте снова:')


@low_router.message(TicketState.destination_city)
async def define_cities(message: Message, state: FSMContext):
    user_data = await state.get_data()
    try:
        destination_city = message.text.strip().lower()
        destination_code = CityMethods.get_city_code(destination_city)
        if destination_code is None:
            await message.answer(text='Ошибка! Некорректно введен город назначения.\n'
                                      'Попробуйте снова:')
        else:
            await state.update_data(destination=destination_code)
            if user_data.get("request") in ["low", "custom"]:
                text = 'Отлично! А теперь введите дату отправления.\n'
            else:
                text = 'Отлично! А теперь введите первое число месяца, для которого хотите найти билеты.'
            await message.answer(text=text,
                                 reply_markup=await start_calendar_kb(message.from_user))

    except Exception:
        await message.answer(text='Ошибка! Некорректно введен город назначения.\n'
                                  'Попробуйте снова:')


@low_router.callback_query(SimpleCalendarCallback.filter())
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: SimpleCalendarCallback,
                                  state: FSMContext):
    calendar = await create_calendar(callback_query.from_user)
    selected, date = await calendar.process_selection(callback_query, callback_data)
    print(selected)
    user_data = await state.get_data()
    if selected:
        if user_data.get("request") in ["low", "custom"]:
            if user_data.get("one_way", None) is None:
                await state.update_data(departure_at=date.strftime("%Y-%m-%d"))

                await callback_query.message.answer(text=f'Вы выбрали {date.strftime("%d/%m/%Y")}.\n'
                                                         f'Вам нужен обратный билет?\n'
                                                         f'Выберите да или нет...', reply_markup=y_n_kb()
                                                    )
                await state.set_state(TicketState.return_ticket)
            else:
                await state.update_data(return_at=date.strftime("%Y-%m-%d"))
                await callback_query.message.answer(text=f'Вы выбрали {date.strftime("%d/%m/%Y")}.\n')
                if user_data.get("request") == "low":
                    api_result = await find_api_results(callback_query.message, state)
                    await answer_to_user(callback_query.message, state, api_result)
                else:
                    await callback_query.message.answer("А теперь выберите признак, "
                                                        "по которому хотите сгруппировать билеты: ",
                                                        reply_markup=group_by_kb())
                    await state.set_state(TicketState.group_by)
        else:
            await state.update_data(month=date.strftime("%Y-%m-%d"))
            await callback_query.message.answer(
                text=f'Результаты будут показаны для месяца, который начинается {date.strftime("%d/%m/%Y")}.\n')
            api_result = await find_api_results(callback_query.message, state)
            await answer_to_user(callback_query.message, state, api_result)




# @low_router.message(TicketState.departure_at)
# async def departure_date(message: Message, state: FSMContext):
#     await state.update_data(departure_at=message.text.strip())
#     await message.answer(text='Вам нужен обратный билет?\n'
#                               'Выберите да или нет...', reply_markup=y_n_kb())
#     await state.set_state(TicketState.return_ticket)


@low_router.message(TicketState.return_ticket)
async def answer_return_ticket(message: Message, state: FSMContext):
    user_data = await state.get_data()
    if message.text.lower() == "да":
        await state.update_data(one_way=False)
        await message.answer(text='Введите дату обратного вылета...',
                             reply_markup=await start_calendar_kb(message.from_user))
    else:
        if user_data.get("request") == "low":
            api_result = await find_api_results(message, state)
            await answer_to_user(message, state, api_result)
        else:
            await message.answer("А теперь выберите признак, "
                                 "по которому хотите сгруппировать билеты: ",
                                 reply_markup=group_by_kb())
            await state.set_state(TicketState.group_by)


# @low_router.message(TicketState.return_at)
# async def return_date(message: Message, state: FSMContext):
#     await state.update_data(return_at=message.text.strip())
#     await show_results(message, state)


@low_router.message(TicketState.count_to_show)
async def counts_to_show(message: Message, state: FSMContext):
    user_data = await state.get_data()
    api_result = user_data.get("api_result")
    try:
        count_to_show = int(message.text.strip())
        if 1 <= count_to_show <= len(api_result):
            await answer_to_user(message, state, api_result, default_num=count_to_show, not_defined_by_user=False)
        else:
            await message.answer(text=f"Ошибка! Введите число в допустимых пределах, максимально - {len(api_result)}")
    except Exception:
        await message.answer(text=f"Ошибка! Введите корректное число, максимально - {len(api_result)}")


@low_router.message(TicketState.change_date)
async def change_dates(message: Message, state: FSMContext):
    if message.text.lower() == "да":
        await state.update_data(one_way=None)
        await message.answer(text='Введите дату отправления',
                             reply_markup=await start_calendar_kb(message.from_user))
    else:
        await message.answer(text="Благодарю за обращение. Завершаю обработку запроса...",
                             reply_markup=main_keyboard())
        await state.clear()


@low_router.callback_query()
async def group_tickets_by(callback: CallbackQuery, state: FSMContext):
    action = callback.data
    if action in ['departure_at', 'return_at', 'month']:
        await state.update_data(group_by=action)
        api_result = await find_api_results(callback.message, state)
        await answer_to_user(callback.message, state, api_result)
    await callback.answer()
