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
                                      f'Я помогу вам с авиабилетами и поищу их на Aviasales.'
                                      f'\nВыберите следующую команду:', reply_markup=main_keyboard())
        else:
            await message.answer(text='Добро пожаловать в бот! '
                                      'Я помогу вам с авиабилетами и поищу их на Aviasales.'
                                      'Поскольку вы в первый раз, напишите, пожалуйста, как к вам обращаться:')
            await state.set_state(UserState.name)
    else:
        print(user[0].name)
        await message.answer(text=f"Рад вас снова видеть, {user[0].name}!\nЧем я могу помочь сегодня? ",
                             reply_markup=main_keyboard())


@default_router.message(UserState.name)
async def get_name(message: Message, state: FSMContext):
    username = message.text
    UserMethods.registrate_user(message.from_user.id, username)
    await message.answer(text='Спасибо! а теперь выберите следующую команду:', reply_markup=main_keyboard())
    await state.clear()


@default_router.message(StateFilter(None), Command("help"))
async def help(message: Message):
    await message.answer(text='Вам доступны следующие действия:\n'
                              '/low - поиск самого дешёвого авиабилета на определенные даты\n'
                              '/high - поиск прямого авиабилета с самой низкой ценой\n'
                              '/custom - поиск самых дешёвых авиабилетов за каждый день периода\n'
                              '/history - просмотр истории поиска (последние 5 запросов)',
                         reply_markup=main_keyboard())


# @default_router.message(StateFilter(TicketState.origin_city,
#                                     TicketState.destination_city,
#                                     TicketState.return_ticket,
#                                     TicketState.change_date), Command("exit"))
# async def exit(message: Message, state: FSMContext):
#     await message.answer(text="Завершаю запрос...")
#     await state.clear()


@default_router.message(StateFilter(None))
async def any_text(message: Message):
    await message.answer(text='Выберите одну из следующих команд:',
                         reply_markup=main_keyboard())










