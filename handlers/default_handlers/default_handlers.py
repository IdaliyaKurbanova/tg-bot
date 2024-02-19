from aiogram import F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.handlers.message import Message
from aiogram.fsm.context import FSMContext
from states.states import UserState, TicketState
from database.utils import *
from keyboards.reply.reply_keyboards import main_keyboard

default_router = Router()


@default_router.message(StateFilter(None), CommandStart())
async def start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user = UserMethods.get_user(user_id)
    print(user)
    if user is None:
        username = message.from_user.username
        if username:
            UserMethods.registrate_user(user_id, username)
            await message.answer(text=f'{username}, добро пожаловать в бот! '
                                      f'Я умею искать билеты на Aviasales.'
                                      f' Для поиска билетов выберите одну из следующих команд:\n'
                                      f'/low - поиск самого дешёвого авиабилета на определенные даты\n'
                                      '/high - поиск прямого авиабилета с самой низкой ценой\n'
                                      '/custom - поиск самых дешёвых авиабилетов за каждый день месяца\n'
                                      '/history - просмотр вашей истории поиска (последние 5 запросов)',
                                 reply_markup=main_keyboard())
        else:
            await message.answer(text='Добро пожаловать в бот! '
                                      'Я умею искать билеты на Aviasales.'
                                      'Поскольку вы в первый раз, напишите, пожалуйста, как к вам обращаться:')
            await state.set_state(UserState.name)
    else:
        print(user[0].name)
        await message.answer(text=f"Рад вас снова видеть, {user[0].name}!\nЧем я могу помочь сегодня? \n"
                                  f"/low - поищу самые дешёвые авиабилеты на определенные даты\n"
                                  f"/high - поищу прямой авиабилет с самой низкой ценой\n"
                                  f"/custom - поищу самый дешёвый авиабилет за каждый день месяца\n"
                                  f"/history - покажу историю вашего поиска (последние 5 запросов)",
                             reply_markup=main_keyboard())


@default_router.message(UserState.name)
async def get_name(message: Message, state: FSMContext):
    username = message.text
    UserMethods.registrate_user(message.from_user.id, username)
    await message.answer(text='Спасибо! а теперь для поиска билета выберите одну из следующих команд:\n'
                              '/low - поиск самого дешёвого авиабилета на определенные даты\n'
                              '/high - поиск прямого авиабилета с самой низкой ценой\n'
                              '/custom - поиск самых дешёвых авиабилетов за каждый день месяца\n'
                              '/history - просмотр вашей истории поиска (последние 5 запросов)',
                         reply_markup=main_keyboard())
    await state.clear()


@default_router.message(StateFilter(None), Command("help"))
async def help(message: Message):
    await message.answer(text='Я бот, который ищет билеты на Aviasales. '
                              'Для поиска билетов выберите одну из следующих команд:\n'
                              '/low - поиск самого дешёвого авиабилета на определенные даты\n'
                              '/high - поиск прямого авиабилета с самой низкой ценой\n'
                              '/custom - поиск самых дешёвых авиабилетов за каждый день периода\n'
                              '/history - просмотр вашей истории поиска (последние 5 запросов)',
                         reply_markup=main_keyboard())


@default_router.message(Command("exit"), StateFilter("*"))
async def exit(message: Message, state: FSMContext):
    await message.answer(text="Завершаю запрос...")
    await state.clear()


@default_router.message(StateFilter(None))
async def any_text(message: Message):
    await message.answer(text='Выберите одну из следующих команд:',
                         reply_markup=main_keyboard())










