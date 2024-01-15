from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from data.config import ADMINS
from modules.database import cardsDB, cardsCurs
from modules.slider import update_price_slides, slides


class AdminState(StatesGroup):
	new_price = State()
	update_price = State()


async def change_price(message: types.Message):
	if message.chat.id in ADMINS:
		await message.answer('Выберите карту, цену которой хотите изменить:\n1. 500\n2. 1000\n3. 1500\n4. 2000\n5. 2500\n6. 3000\n7. 3500\n8. 4000')
		await AdminState.new_price.set()
	else:
		await message.answer(f'У вас нет доступа к этой команде.')


async def new_price(message: types.Message, state: FSMContext):
	try: 
		await state.update_data(nominal=slides[int(message.text)-1][0])
		await message.answer('Укажите новую стоимость карты:')
		await AdminState.update_price.set()
	except ValueError:
		await message.answer('Введите только число!')


async def update_price(message: types.Message, state: FSMContext):
	try: 
		user_data = await state.get_data()
		price = cardsCurs.execute(f'UPDATE prices SET price={int(message.text)} WHERE nominal='+str(user_data['nominal']))
		cardsDB.commit()
		update_price_slides(cardsCurs)
		await state.finish()
		await message.answer('Цена успешно обновлена!')
	except ValueError:
		await message.answer('Введите только число!')


def register_admin_panel(dp: Dispatcher):
	dp.register_message_handler(change_price, commands='newprice')
	dp.register_message_handler(new_price, state=AdminState.new_price)
	dp.register_message_handler(update_price, state=AdminState.update_price)