from aiogram import Dispatcher, types
from modules.keyboards import *
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

# Номиналы и их слайды (Сделано для упрощения работы слайдера).
nominal = {'500': 0, '1000': 1, '1500': 2, '2000': 3, '2500': 4, '3000': 5, '3500': 6, '4000': 7}

# Слайды (№: номинал, фото, цена).
slides = {0: [500, 'photos/nominals/500.png', 0], 
		1: [1000, 'photos/nominals/1000.png', 0], 
		2: [1500, 'photos/nominals/1500.png', 0], 
		3: [2000, 'photos/nominals/2000.png', 0],
		4: [2500, 'photos/nominals/2500.png', 0], 
		5: [3000, 'photos/nominals/3000.png', 0], 
		6: [3500, 'photos/nominals/3500.png', 0], 
		7: [4000, 'photos/nominals/4000.png', 0], 
	}

# Обновление цены карт на слайдах.
def update_price_slides(cardsCurs):
	for i in slides:
		nom = slides[i][0]
		price = cardsCurs.execute('SELECT price FROM prices WHERE nominal='+str(nom)).fetchall()[0][0]
		slides[i][2] = price


# Оформление слайда.
def create_slide(photo, nominal, price):
	return types.InputMediaPhoto(types.InputFile(photo), caption=f'<b>Карта iTunes - {nominal} руб.</b>\n\nСтоимость карты {price} рублей. Для покупки нажмите "Купить".\n\nДля того, чтобы выбрать другой номинал карты, листайте вправо или влево.')


# Изменение слайда (вперед, назад).
async def next_slide(call: types.CallbackQuery):
	n_slide = nominal[''.join(filter(str.isdigit, call.message.caption.split('.')[0]))]

	if call.data == 'cb_forw':
		n_slide += 1
		if n_slide == len(slides):
			n_slide = 0

	elif call.data == 'cb_back':
		n_slide -= 1
		if n_slide < 0:
			n_slide = len(slides)-1

	slide = slides[n_slide]
	await call.message.edit_media(create_slide(slide[1], slide[0], slide[2]), reply_markup=inline_menu)


# Кнопка «Купить».
async def start_slider(call: types.Message, state: FSMContext):
	await state.finish()
	await call.message.edit_media(create_slide(slides[0][1], slides[0][0], slides[0][2]), reply_markup=inline_menu)


def register_slider(dp: Dispatcher):
	dp.register_callback_query_handler(start_slider, text='cb_slider', state='*')
	dp.register_callback_query_handler(next_slide, text=['cb_back', 'cb_forw'])