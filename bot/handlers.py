from aiogram import types
from aiogram.dispatcher import FSMContext
from .states import TicketCreate
from . import bot, dp
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

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

names: list[str] = ['Ольга', 'Ирина', 'Елена']


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
    print(f'State in start_callback: {current_state}')

    await subdivision_show(callback, state)
    await callback.answer()
    await TicketCreate.next()


async def create_buttons(item_array):
    keyboard = InlineKeyboardMarkup(row_width=3)
    for item in item_array:
        cd = item
        btn = InlineKeyboardButton(text=item, callback_data=cd)
        keyboard.add(btn)
    return keyboard


async def confirm_pick(chat_id):
    keyboard = InlineKeyboardMarkup(
        InlineKeyboardButton(text="Да", callback_data="confirm_yes"),
        InlineKeyboardButton(text="Нет", callback_data="confirm_no")
    )

    await bot.send_message(chat_id, "Подтвердить выбор", reply_markup=keyboard)


@dp.callback_query_handler(state=TicketCreate.start)
async def subdivision_show(callback, state):
    current_state = await state.get_state()
    print(f'Состояние в subdivision_show {current_state}')
    keyboard = await create_buttons(subdivision)
    await bot.send_message(callback.from_user.id, text='Укажите подразделение:',
                           reply_markup=keyboard)


@dp.callback_query_handler(state=TicketCreate.division)
async def division_pick(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['division'] = call.data

    await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
    await bot.edit_message_text(f"Выбранное подразделение: {data['division']}",
                                call.message.chat.id, call.message.message_id)
    await TicketCreate.next()
    await call.answer()

    keyboard = await create_buttons(names)
    await confirm_pick(call.message.chat.id)
    await bot.send_message(call.message.chat.id, "Выберите ваше имя:",
                           reply_markup=keyboard)


@dp.callback_query_handler(state=TicketCreate.full_name)
async def pick_name(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['pick_name'] = call.data
    await bot.edit_message_text(f'Выбранный сотрудник: {data["pick_name"]}',
                                call.message.chat.id, call.message.message_id)
    await TicketCreate.next()
    await call.answer()
