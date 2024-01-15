from aiogram import Bot, Dispatcher, types

from data.config import TOKEN
from modules.database import storage


# Подключение API Telegram.
print('Подключение API Telegram...')
bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)