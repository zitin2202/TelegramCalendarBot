from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import  ReplyKeyboardMarkup, KeyboardButton
import os


bot = Bot(token=os.getenv(("Token")))
storage = MemoryStorage()
dp = Dispatcher(bot,storage = storage)

b1 = KeyboardButton('/start')
b2 = KeyboardButton('/connect')
b3 = KeyboardButton('/create')
b4 = KeyboardButton('/cancel')

kb_menu = ReplyKeyboardMarkup(resize_keyboard=True)
kb_menu.row(b1,b2).row(b3,b4)