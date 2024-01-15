import random, string
from aiogram import Dispatcher, types
from modules.keyboards import *
from modules.dialogs import *
from data.config import ADMINS
from modules.database import cardsDB, cardsCurs



async def generate_ref_code(message: types.Message):
    if message.chat.id in ADMINS:
        letters = string.ascii_lowercase + string.digits
        ref_code = ''.join(random.choice(letters) for i in range(10))
        cardsCurs.execute('INSERT INTO ref_system (code) VALUES (?)', (str(ref_code),))
        cardsDB.commit()
        await message.answer(f"Уникальный id рекламы {ref_code}")
        await message.answer_photo(types.InputFile('photos/ref_image.jpg'), caption=ref_text, reply_markup=create_ref_kb(ref_code))


async def get_activate_count(message: types.Message):
    if message.chat.id in ADMINS:
        ref_code = message.get_args()
        get_count = cardsCurs.execute(f'SELECT count FROM ref_system where code=(?)', (ref_code,)).fetchone()
        await message.bot.send_message(chat_id=message.from_user.id,text=f"Код: {ref_code}\nИспользовали: {get_count[0]} раз")


# Команда «start».
async def start(message: types.Message):
    ref_code_start = message.get_args()
    if ref_code_start:
        check_used = cardsCurs.execute('SELECT*from ref_used where ref_code=(?) and who_used_id=(?)',(ref_code_start,message.from_user.id,)).fetchall()
        if not check_used:
            get_count = cardsCurs.execute(f'SELECT count FROM ref_system where code=(?)',(ref_code_start,)).fetchone()
            new_count = get_count[0]+1
            cardsCurs.execute(f"update ref_system set count=(?) where code=(?)",(new_count,ref_code_start,))
            cardsCurs.execute('INSERT INTO ref_used (ref_code,who_used_id) VALUES (?,?)', (ref_code_start,message.from_user.id,))
            cardsDB.commit()
    await message.answer_photo(types.InputFile('photos/logo.jpg'), caption=start_text, reply_markup=menu)


# Кнопка «О нас».
async def about(call: types.CallbackQuery):
    await call.message.delete()
    await call.message.answer(about_text, reply_markup=back_menu)


# Кнопка «FAQ».
async def faq(call: types.CallbackQuery):
    await call.message.delete()
    await call.message.answer(faq_text, reply_markup=faq_menu)


# Кнопка «Контакты».
async def contact(call: types.CallbackQuery):
    await call.message.delete()
    await call.message.answer(contact_text, reply_markup=back_menu)


async def backs(call: types.Message):
    await call.message.edit_media(types.InputMediaPhoto(types.InputFile('photos/logo.jpg'), caption=start_text),
                                  reply_markup=menu)


async def backm(call: types.Message):
    await call.message.delete()
    await start(call.message)


def register_menu(dp: Dispatcher):
    dp.register_message_handler(start, commands='start')
    dp.register_message_handler(generate_ref_code, commands='generate_ref_code')
    dp.register_message_handler(get_activate_count, commands='get_activation')
    dp.register_callback_query_handler(about, text='cb_about')
    dp.register_callback_query_handler(faq, text='cb_faq')
    dp.register_callback_query_handler(contact, text='cb_contact')
    dp.register_callback_query_handler(backs, text='cb_backs')
    dp.register_callback_query_handler(backm, text='cb_backm')
