from aiogram import types
from modules.dialogs import *

# Объявление основного inline-меню.
menu = types.InlineKeyboardMarkup()
menu.add(types.InlineKeyboardButton(buy_bttn, callback_data='cb_slider'))
menu.add(types.InlineKeyboardButton(about_bttn, callback_data='cb_about'))
menu.add(types.InlineKeyboardButton(feedback_bttn, callback_data='cb_feedback'))
menu.add(types.InlineKeyboardButton(faq_bttn, callback_data='cb_faq'), types.InlineKeyboardButton(contact_bttn, callback_data='cb_contact'))

# Объявление inline-меню слайдера.
inline_menu = types.InlineKeyboardMarkup()
inline_menu.add(types.InlineKeyboardButton(left_bttn, callback_data='cb_back'), types.InlineKeyboardButton(right_bttn, callback_data='cb_forw'))
inline_menu.add(types.InlineKeyboardButton(buy_bttn, callback_data='cb_buy'))
inline_menu.add(types.InlineKeyboardButton(back_bttn, callback_data='cb_backs'))

# Объявление меню из слайдера в главное меню.
backs_menu = types.InlineKeyboardMarkup()
backs_menu.add(types.InlineKeyboardButton(back_bttn, callback_data='cb_backs'))

# Объявление меню из подменю в главное меню.
back_menu = types.InlineKeyboardMarkup()
back_menu.add(types.InlineKeyboardButton(back_bttn, callback_data='cb_backm'))

# Объявление меню после успешной покупки.
pay_back_menu = types.InlineKeyboardMarkup()
pay_back_menu.add(types.InlineKeyboardButton('Оставить отзыв', callback_data='cb_new_feedback'))
pay_back_menu.add(types.InlineKeyboardButton(back_bttn, callback_data='cb_backs'))

# Объявление меню для слайдера отзывов.
feedback_menu = types.InlineKeyboardMarkup()
feedback_menu.add(types.InlineKeyboardButton(left_bttn, callback_data='cb_feed_back'), types.InlineKeyboardButton(right_bttn, callback_data='cb_feed_forw'))
feedback_menu.add(types.InlineKeyboardButton(back_bttn, callback_data='cb_backs'))

# Объявление меню для отображения имени в отзыве.
name_include_menu = types.InlineKeyboardMarkup()
name_include_menu.add(types.InlineKeyboardButton('Да', callback_data='cb_feed_yes'), types.InlineKeyboardButton('Нет', callback_data='cb_feed_no'))

# Объявление меню для менедежера при проверке отзыва.
feed_check_menu = types.InlineKeyboardMarkup()
feed_check_menu.add(types.InlineKeyboardButton('Отклонить', callback_data='cb_feed_delete'), types.InlineKeyboardButton('Прикрепить фото', callback_data='cb_feed_add'))

# Объявление меню FAQ.
faq_menu = types.InlineKeyboardMarkup()
faq_menu.add(types.InlineKeyboardButton(feedback_bttn, callback_data='cb_feedback_faq'))
faq_menu.add(types.InlineKeyboardButton(back_bttn, callback_data='cb_backm'))

def create_ref_kb(ref_code):
	ref_kb = types.InlineKeyboardMarkup()
	ref_kb.add(types.InlineKeyboardButton("Перейти", url='https://t.me/igiftcard_bot?start='+ref_code))
	return ref_kb
# Создание inline-меню для оплаты счёта.
def create_buy_menu(url):
	buy_menu = types.InlineKeyboardMarkup()
	buy_menu.add(types.InlineKeyboardButton(pay_bttn, url=url))
	buy_menu.add(types.InlineKeyboardButton(check_bttn, callback_data='cb_pay'))
	buy_menu.add(types.InlineKeyboardButton(back_bttn, callback_data='cb_slider'))
	return buy_menu