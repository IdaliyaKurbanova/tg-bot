from aiogram import F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.handlers.message import Message
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from states.states import TicketState
from siteAPI_info import APIResult
from database.utils import CityMethods, HistoryMethods
from keyboards.reply.reply_keyboards import y_n_kb, main_keyboard
from keyboards.inline.inline_keyboards import site_url_kb
import json

high_router = Router()



