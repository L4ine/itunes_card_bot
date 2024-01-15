import asyncio
import logging
import traceback

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext

from modules.loader import dp, bot
from modules.database import storage, cardsCurs, cardsDB
from modules.payment import register_payment
from modules.admin_panel import register_admin_panel
from modules.menu import register_menu
from modules.slider import register_slider, update_price_slides
from modules.feedback import register_feedback
from modules.error_handler import register_error


async def main():
	# Подключение логгирования.
	print('Подключение логгирования...')
	logging.basicConfig(filename='data/bot.log', format='[%(levelname)s] %(asctime)s - %(message)s', datefmt='%d/%b/%y %H:%M:%S')
	
	await bot.set_my_commands([types.BotCommand('start', 'Запуск бота.')])
	register_error(dp)
	register_menu(dp)
	register_slider(dp)
	register_feedback(dp)
	register_payment(dp)
	register_admin_panel(dp)
	update_price_slides(cardsCurs)

	try:
		print('Бот начал работу...')
		logging.info('The bot is running...')
		await dp.start_polling()
	finally:
		cardsDB.close()
		await dp.storage.close()
		await dp.storage.wait_closed()
		await bot.session.close()

# Запуск.
if __name__ == "__main__":
	try:
		asyncio.run(main())
	except (KeyboardInterrupt, SystemExit):
		logging.error('Bot stopped!')
	except:
		logging.error(traceback.format_exc())
