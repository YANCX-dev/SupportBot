from aiogram import types
from aiogram.dispatcher import FSMContext
from .states import TicketCreate
from . import bot, dp
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

division: list[str] = ['СВК 501 Каменка',
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

names: list[str] = ['Ольга', 'Ирина', 'Елена']


@dp.callback_query_handler(state=TicketCreate.confirmation)
async def confirm_choice(call: types.CallbackQuery, state: FSMContext):
    if call.data == "division_confirm_yes":
        current_state = state.get_state()
        print(f'1 {current_state}')
        await TicketCreate.next()
        print(f'2 {current_state}')


@dp.message_handler(commands=['start'], state=None)
async def start_message(message: types.Message, state: FSMContext):
    # if (message.from_user.id) // only registered users can use the bot
    current_state = await state.get_state()
    print(f'Состояние в start_message: {current_state}')
    keyboard = InlineKeyboardMarkup()
    button = InlineKeyboardButton(text='Да', callback_data='start_yes')
    keyboard.add(button)
    await message.answer('Добрый день! Вы обратились в техподдержку.\nХотите оформить обращение или проверить статус?',
                         reply_markup=keyboard)

    await TicketCreate.next()


@dp.callback_query_handler(text='start_yes', state=TicketCreate.start)
async def start_callback(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    print(f'State in start_callback: {current_state}')
    await show_division(callback, division)
    await callback.answer()
    await TicketCreate.next()


async def show_division(call, div):
    keyboard = await create_buttons(div)
    await bot.send_message(call.message.chat.id, "Укажите подразделение:",
                           reply_markup=keyboard)


@dp.callback_query_handler(state=TicketCreate.division)
async def division_pick(call: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    async with state.proxy() as data:
        data['p_division'] = call.data
        data[f'{current_state.split(":")[1]}'] = current_state.split(':')[1]
    await state.set_state(TicketCreate.confirmation)
    await confirm_pick(call.message.chat.id, call.message.message_id, data)
    await call.answer()


async def create_buttons(item_array):
    keyboard = InlineKeyboardMarkup(row_width=3)
    for item in item_array:
        cd = item
        btn = InlineKeyboardButton(text=item, callback_data=cd)
        keyboard.add(btn)
    return keyboard


async def confirm_pick(chat_id, message_id, data):
    btn1 = InlineKeyboardButton(text="Да", callback_data=f'confirm_yes')
    btn2 = InlineKeyboardButton(text="Нет", callback_data=f'confirm_no')
    kb = InlineKeyboardMarkup()
    kb.add(btn1, btn2)
    print(kb)
    print("Я ПОПАЛ В ФУНКЦИЮ ПОДТВЕРЖДЕНИЯ confirm_pick: " + f'1')
    await bot.send_message(chat_id, f'Вы уверены, что хотите выбрать {data["p_division"]} ?', reply_markup=kb)
    # btn1 = InlineKeyboardButton(text="Да", callback_data=f'{data}_confirm_yes')
    # btn2 = InlineKeyboardButton(text="Нет", callback_data=f'{data}_confirm_no')
    # keyboard = InlineKeyboardMarkup()
    # keyboard.add(btn1, btn2)
    # print(chat_id)
    # await bot.send_message(chat_id, f'Вы уверены что хотите подтвердить выбор - {data[data]} ?')
    # await bot.delete_message(chat_id, message_id)


    # await bot.edit_message_reply_markup(chat_id, msg['from'].id, reply_markup=keyboard)
