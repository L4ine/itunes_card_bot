import os, random
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from data.config import MANAGER
from modules.loader import bot
from modules.database import cardsDB, cardsCurs
from modules.keyboards import *


class FeedbackState(StatesGroup):
	name_include = State()
	new_feed = State()
	new_photo = State()


def update_feedback():
	data = {}
	feed_photo = cardsCurs.execute('SELECT photo FROM feedbacks').fetchall()
	feed_text = cardsCurs.execute('SELECT text FROM feedbacks').fetchall()
	num = [i for i in range(len(feed_photo))]

	for i in num:
		data.update({i: [feed_text[i][0], feed_photo[i][0]]})

	return data


async def delete_feedback(call: types.CallbackQuery):
	await call.message.delete()


async def add_feedback(call: types.CallbackQuery, state: FSMContext):
	await call.message.answer('Отправьте фотографию...')
	await state.update_data(text=call.message.text)
	await FeedbackState.new_photo.set()


async def add_photo(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		text = data.get('text')

	cardsCurs.execute('INSERT INTO feedbacks (id, text, photo) VALUES (?, ?, ?)', (message.message_id, text, message.photo[-1].file_id))
	cardsDB.commit()

	await message.delete()
	await message.answer('Отзыв добавлен.')
	await state.finish()


async def new_feedback(call: types.CallbackQuery, state: FSMContext):
	await call.message.edit_caption('Напишите о своём положительном или негативном опыте использования бота iGiftcard.', reply_markup=backs_menu)
	await state.update_data(call_id=call)
	await FeedbackState.name_include.set()


async def name_include(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		call_id = data.get('call_id')
		await call_id.message.delete()

	await message.answer('Хотите ли оставить в комментарии свой никнейм?', reply_markup=name_include_menu)
	await state.update_data(feed=message.text)
	await FeedbackState.new_feed.set()


async def send_feedback(call: types.CallbackQuery, state: FSMContext):
	await call.message.delete()
	async with state.proxy() as data:
		feed = data.get('feed')

	if call.data == 'cb_feed_yes':
		name = '@'+call.message.chat.username+': '

	elif call.data == 'cb_feed_no':
		name = 'Пользователь: '

	await call.message.answer('Спасибо, что оставили свой отзыв!', reply_markup=back_menu)

	await state.finish()
	await bot.send_message(MANAGER, name+feed, reply_markup=feed_check_menu)


# Изменение слайда (вперед, назад).
async def next_feedback(call: types.CallbackQuery):
	slides = update_feedback()
	n_slide = int(''.join(call.message.caption.split('/')[0]))-1

	if call.data == 'cb_feed_forw':
		n_slide += 1
		if n_slide == len(slides):
			n_slide = 0

	elif call.data == 'cb_feed_back':
		n_slide -= 1
		if n_slide < 0:
			n_slide = len(slides)-1

	await call.message.edit_media(types.InputMediaPhoto(slides[n_slide][1], f'{n_slide+1}/{len(slides)}. {slides[n_slide][0]}'), reply_markup=feedback_menu)


# Кнопка «Купить».
async def start_feedback(call: types.Message):
	slides = update_feedback()
	if call.data == 'cb_feedback_faq':
		await call.message.delete()
		await call.message.answer_photo(slides[0][1], f'1/{len(slides)}. {slides[0][0]}', reply_markup=feedback_menu)
	elif call.data == 'cb_feedback':
		await call.message.edit_media(types.InputMediaPhoto(str(slides[0][1]), f'1/{len(slides)}. {slides[0][0]}'), reply_markup=feedback_menu)


def register_feedback(dp: Dispatcher):
	dp.register_callback_query_handler(start_feedback, text=['cb_feedback', 'cb_feedback_faq'])
	dp.register_callback_query_handler(next_feedback, text=['cb_feed_back', 'cb_feed_forw'])
	dp.register_callback_query_handler(new_feedback, text='cb_new_feedback')
	dp.register_message_handler(name_include, state=FeedbackState.name_include)
	dp.register_callback_query_handler(send_feedback, text=['cb_feed_yes', 'cb_feed_no'], state=FeedbackState.new_feed)
	dp.register_callback_query_handler(delete_feedback, text='cb_feed_delete')
	dp.register_callback_query_handler(add_feedback, text='cb_feed_add')
	dp.register_message_handler(add_photo, content_types='photo', state=FeedbackState.new_photo)
