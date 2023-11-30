from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from dotenv import load_dotenv, find_dotenv
import os
import logging

load_dotenv(find_dotenv())
storage = MemoryStorage()
bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher(bot, storage=storage)

logging.basicConfig(level=logging.INFO)


async def on_start_up(_):
    print('Bot has been started')


subdivision: list[str] = ['СВК 501 Каменка',
                          'СВК 502 Каменка',
                          'СВК 601 Березовка',
                          'СВК 602 Березовка',
                          'СВК 701 Красноселка',
                          'СВК 702 Красноселка',
                          'СВК 801 Михири',
                          'СВК 802 Михири',
                          'СВК Березовка-1',
                          'СВК Калиновка/Рождественка',
                          'СВК Ключи',
                          'СВК Михири-1',
                          'СВК-1',
                          'СВК-2',
                          'СВК-3']  # Временные подразделения


class TicketCreate(StatesGroup):
    sub_div = State()
    full_name = State()
    category = State()
    description = State()


@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    # if (message.from_user.id) // only registered users can use the bot
    keyboard = InlineKeyboardMarkup()
    button = InlineKeyboardButton(text='Да', callback_data='start_yes')
    keyboard.add(button)
    await message.answer('Добрый день! Вы обратились в техподдержку.\nХотите оформить обращение или проверить статус?',
                         reply_markup=keyboard)


@dp.callback_query_handler(text='start_yes')
async def start_callback(callback: types.CallbackQuery):
    await subdivision_show(callback)


async def subdivision_show(callback):
    keyboard = InlineKeyboardMarkup(row_width=3)
    for item in subdivision:
        cd = f'button_{item.lower().replace(" ", "_")}'
        btn = InlineKeyboardButton(text=item, callback_data=cd)
        keyboard.add(btn)
    await bot.send_message(callback.from_user.id, text='Укажите подразделение:', reply_markup=keyboard)


# @dp.callback_query_handler(content_types=['sub_div'], state=TicketCreate.sub_div)
# async def subdivision_pick(callback: types.CallbackQuery, state: FSMContext):
#     btn_data = callback.data.split('_')
#     _subdivision = ' '.join(btn_data[1:])
#     async with state.proxy() as data:
#         data['sub_div'] = callback.sub_div
#
#     await TicketCreate.sub_div.set()
#     await callback.answer()


# @dp.message_handler()
# async def select(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:


if __name__ == '__main__':
    executor.start_polling(dispatcher=dp,
                           skip_updates=True,
                           on_startup=on_start_up)
