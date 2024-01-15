from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from pygsheets import authorize

from glQiwiApi import QiwiP2PClient
from glQiwiApi.qiwi.clients.p2p.types import Bill

from data.config import ADMIN_CHAT, COMMENT, QIWI_TOKEN, TABLE_NAME
from modules.loader import bot
from modules.database import cardsCurs
from modules.slider import nominal
from modules.keyboards import *
from modules.dialogs import *


# Подключение Google Sheets API.
print('Подключение Google Sheets API...')
google = authorize(service_file='data/google_credentials.json')
sheet = google.open(TABLE_NAME)
worksheet = sheet.worksheet('index', 0)

# Подключение Qiwi P2P API.
print('Подключение Qiwi P2P API...')
qiwi_p2p_client = QiwiP2PClient(secret_p2p=QIWI_TOKEN)

class PaymentState(StatesGroup):
	check_pay = State()


# Проверка доступности выдачи карты.
def check_availability(nom):
	needs = []
	# Получение кол-во карт каждого номинала.
	availability = worksheet.get_all_values(majdim='columwise', include_tailing_empty=False, include_tailing_empty_rows=False)
	cards = dict(zip([4000, 3500, 3000, 2500, 2000, 1500, 1000, 500], [len(i)-1 for i in availability][::-1]))
	available_card = [k for k in cards if k <= nom and cards[k] > 0]
	sum_cards = sum([key*value for key, value in cards.items() if key <= nom])

	if sum_cards < nom:
		return None
	else:
		while sum(needs) != nom:
			for i in available_card:
				if sum(needs)+i <= nom:
					cards[i] -= 1
					needs.append(i)
				else:
					available_card.remove(i)

					if sum(needs) == nom:
						break

					elif len(available_card) == 1 and sum(needs)+available_card[0] != nom:
						return None
	return needs


# Оповещение админов о успешной покупке карты.
async def notify_admin(message, username, nom, price, card):
	await bot.send_message(ADMIN_CHAT, f'✅ @{username} успешно купил карту номиналом {nom} за {price} руб.\n\n💳 Выданные карты: '+', '.join(card))


# Создание счёта в зависимости от номинала.
async def handle_creation_of_payment(call: types.CallbackQuery, state: FSMContext):
	nom = ''.join(filter(str.isdigit, call.message.caption.split('.')[0]))
	price = cardsCurs.execute('SELECT price FROM prices WHERE nominal='+nom).fetchall()[0][0]

	needs = check_availability(int(nom))

	if needs == None:
		await call.message.edit_caption(card_out.format(nom), reply_markup=backs_menu)

	else:
		async with qiwi_p2p_client as p2p:
			bill = await p2p.create_p2p_bill(amount=price, comment=COMMENT, pay_source_filter=['qw', 'card', 'mobile'])
			await state.update_data(bill=bill, needs=needs)
		
		await call.message.edit_caption(pay_info.format(nom, price), reply_markup=create_buy_menu(bill.pay_url))
		await PaymentState.check_pay.set()


# Проверка оплаты счёта, при успешной - выдача карты.
async def handle_successful_payment(call: types.CallbackQuery, state: FSMContext):
	async with state.proxy() as data:
		bill = data.get('bill')
		needs = data.get('needs')

	if await qiwi_p2p_client.check_if_bill_was_paid(bill):
		await state.finish()
		card = []

		for need in needs:
			col = worksheet.get_col(nominal[str(need)]+1, include_tailing_empty=False)

			if len(col)-1 > 0:
				card.append(col[-1])
				worksheet.update_value((len(col), nominal[str(need)]+1), '')
			else:
				await call.message.answer(f'Карты номиналом в {need} закончились. Обратитесь в поддержку...')

		if len(needs) == 1:
			text = f'✅ Оплата прошла успешно!\n\n💳 ID вашей карты: `'+''.join(card)+'`'
		else:
			text = f'✅ Оплата прошла успешно!\n\n💳 Карты на {sum(needs)} не было, поэтому вы получили несколько карт равной этой сумме.\n\nID ваших карт: `'+'`, `'.join(card)+'`'

		await call.message.edit_media(types.InputMediaPhoto(types.InputFile('photos/instruction.png'), caption=text, parse_mode=types.ParseMode.MARKDOWN), reply_markup=pay_back_menu)
		await notify_admin(call.message, call.message.chat.username, sum(needs), bill.amount.value, card)
	else:
		await call.answer('Оплата ещё не выполнена.')


def register_payment(dp: Dispatcher):
	dp.register_callback_query_handler(handle_creation_of_payment, text='cb_buy')
	dp.register_callback_query_handler(handle_successful_payment, text='cb_pay', state=PaymentState.check_pay)
