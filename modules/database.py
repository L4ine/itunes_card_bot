import sqlite3

from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# Подключение базы данных.
print('Подключение базы данных...')
cardsDB = sqlite3.connect('data/data.db', check_same_thread=False)
cardsCurs = cardsDB.cursor()

# Подключение хранилища для FMS.
print('Подключение хранилища...')
storage = MemoryStorage()
