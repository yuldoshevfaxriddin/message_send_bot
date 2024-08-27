import asyncio
import logging
import sys
from os import getenv
import requests

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

# Bot token can be obtained via https://t.me/BotFather
TOKEN = getenv("TOKEN")
telegram_file_information = f"https://api.telegram.org/bot{TOKEN}/getFile?file_id="
telegram_file_path = f"https://api.telegram.org/file/bot{TOKEN}/"

# All handlers should be attached to the Router (or Dispatcher)


client = {
    'name':'Tojiyev Sardor',
    'phone_number':'998932840470',
    'olgan_muddati':'20.12.2024',
    'tolov_muddati':'27.12.2024',
    'qarzi':'30000',
}

TEXT = """full name;number;date;qarz;description
Saidov Xudoshkur;998931234567;12.12.2024;100 ming;
Sadiqov Tohir;998931234567;13.12.2024;200 ming;
Sadullayev Sherzod;998931234567;12.12.2024;15 ming ;
Axmedov Maxmudjon;998931234567;11.122024;20 ming;
Abdullayev Artur;998931234567;10.12.2024;87 ming;"""

MESSAGE1 = """"
Hurmatli Saidov Xudoshkur siz "Baraka Marketdan" 
12.12.2024 da 100 ming sum qarz qilgansiz, shuni 
15.12.2024 gacha to'lashingizni so'raymiz.
"""
MESSAGE2 = """
Baraka Market dan
Saidov Xudoshkur 12.12.2024 kuni 100 ming qarz qilingan
15.12.2024 gacha to'lashingizni so'raymiz.
"""
async def get_telegram_file_information(file_id: str) -> dict:
    respons = requests.get(telegram_file_information+file_id)
    if respons.status_code == 200:
        return {
            'status':'succes',
            'data':respons.json().get('result').get('file_path')
            }
    return {
        'status':'error',
        'data':''
    }

async def get_telegram_file_data_reader(file_path: str) -> dict:
    respons = requests.get(telegram_file_path+file_path)
    if respons.status_code == 200:
        return {
            'status':'succes',
            'data':respons.text
        }
    return {
        'status':'error',
        'data':''
    }

async def convert_text_to_object(text: str) -> list:
    lines = text.split('\n')
    users = []
    for index, line in enumerate(lines):
        data = line.split(';')
        if index == 0 or len(data) < 4:
            continue
        print("data topildi: ",data)
        user = {
            'name':data[0],
            'tel_number':data[1],
            'date':data[2],
            'price':data[3],
            'description':'',
            }
        users.append(user)
    return users


async def send_SMS_message(text: str, number: str) -> bool:
    # habar yuborishkodi 
    print(number, text)
    return True

async def send_message(users:dict)->bool:
    for user in users:
        number = user['tel_number']
        message = f"""Baraka Market dan 
        {user['name']} 12.12.2024 kuni {user['price']} qarz qilingan
        {user['date']} gacha to'lashingizni so'raymiz."""
        status = await send_SMS_message(number=number,text=message)

dp = Dispatcher()

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


@dp.message()
async def echo_handler(message: Message) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    file = message.document
    if file:
        file_information = await get_telegram_file_information(file.file_id)
        if file_information['status'] == 'error':
            await message.answer("file malumoti topilmadi")
            return
        file_data = await get_telegram_file_data_reader(file_information['data'])
        if file_data['status'] == 'error':
            await message.answer("file malumotlari o'qilmadi")
            return
        users = await convert_text_to_object(file_data['data'])
        await send_message(users)
        await message.answer(f"{len(users)} ta odam aniqlandi")

    try:
        # Send a copy of the received message
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Nice try!")


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main(),debug=False)