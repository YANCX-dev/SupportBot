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

options = [
    {"text": "Создать обращение", "callback_data": "create_req"},
    {"text": "Проверить статус", "callback_data": "check_status"}
]
categories = [
    {"text": "1С:Селекция", "callback_data": "1c_pig"},
    {"text": "1С:УПП", "callback_data": "1c_upp"},
    {"text": "Моб приложение Ariant Pig", "callback_data": "mobile_app"},
    {"text": "Интернет, связь", "callback_data": "internet_connect"},
    {"text": "Оборудование", "callback_data": "equipment"}
]

# TODO: TicketCreate rename to StateMachine

@dp.callback_query_handler(state=TicketCreate.confirmation)
async def confirm_choice(call: types.CallbackQuery, state: FSMContext):
    print(f'CONFiRM_CHOICE CALL {call.data}')
    async with state.proxy() as data:
        if call.data == "division_confirm_yes":
            await bot.edit_message_text(f"Выбранное подразделение: <b>{data['p_division']}</b>", call.message.chat.id,
                                        call.message.message_id, parse_mode='HTML')
            await state.set_state(TicketCreate.employee)
            await show_employee(call, names)
            await call.answer()

        elif call.data == "division_confirm_no":
            await state.set_state(TicketCreate.division)
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            await show_division(call, division)

        elif call.data == "employee_confirm_yes":
            await state.set_state(TicketCreate.request_menu)
            cs = await state.get_state()
            print(f'STATE {cs}')
            await bot.edit_message_text(f'Сотрудник: <b>{data["p_employee"]}</b>', call.message.chat.id,
                                        call.message.message_id, parse_mode='HTML')
            await display_options(call, options)

        elif call.data == "employee_confirm_no":
            await state.set_state(TicketCreate.employee)
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            await show_employee(call, names)


async def create_buttons(item_array):
    keyboard = InlineKeyboardMarkup(row_width=3)
    for item in item_array:
        cd = item
        btn = InlineKeyboardButton(text=item, callback_data=cd)
        keyboard.add(btn)
    return keyboard


async def create_keyboard(options_obj):
    keyboard_markup = InlineKeyboardMarkup(row_width=1)

    for button_data in options_obj:
        keyboard_markup.add(
            InlineKeyboardButton(text=button_data["text"], callback_data=button_data["callback_data"])
        )

    return keyboard_markup


async def show_division(call, div_list):
    keyboard = await create_buttons(div_list)
    await bot.send_message(call.message.chat.id, "Укажите подразделение:",
                           reply_markup=keyboard)


async def show_employee(call, employee_list):
    keyboard = await create_buttons(employee_list)
    await bot.send_message(call.message.chat.id, "Укажите ФИО",
                           reply_markup=keyboard)


# @dp.callback_query_handler(state=TicketCreate.request_menu)
async def show_categories(call, category_list):
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    kb = await create_keyboard(category_list)
    print(f'KB IN SHOW CATEGORIES: {kb}')
    await bot.send_message(call.message.chat.id, "Выберите категорию",
                           reply_markup=kb)


async def display_options(call, option_btn_list):

    keyboard = await create_keyboard(option_btn_list)
    print(f'KB IN DISPLAY_OPTIONS: {keyboard}')
    await bot.send_message(call.message.chat.id, "Выберите действие:",
                           reply_markup=keyboard)


async def confirm_pick(chat_id, message_id, data_state, data):
    btn1 = InlineKeyboardButton(text="Да", callback_data=f'{data_state}_confirm_yes')
    btn2 = InlineKeyboardButton(text="Нет", callback_data=f'{data_state}_confirm_no')
    kb = InlineKeyboardMarkup()
    kb.add(btn1, btn2)
    await bot.delete_message(chat_id, message_id)
    await bot.send_message(chat_id, f'Подтвердить выбор: {data} ?', reply_markup=kb)


@dp.message_handler(commands=['start'], state=None)
async def start_message(message: types.Message):
    # if (message.from_user.id) // only registered users can use the bot
    # current_state = await state.get_state()
    # print(f'Состояние в start_message: {current_state}')
    keyboard = InlineKeyboardMarkup()
    button = InlineKeyboardButton(text='Да', callback_data='start_yes')
    keyboard.add(button)
    await message.answer('Добрый день! Вы обратились в техподдержку.\nХотите оформить обращение или проверить статус?',
                         reply_markup=keyboard)

    await TicketCreate.next()


@dp.callback_query_handler(text='start_yes', state=TicketCreate.start)
async def start_callback(callback: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)

    # current_state = await state.get_state()
    # print(f'Состояние в start_callback: {current_state}')
    await TicketCreate.next()
    await show_division(callback, division)
    await callback.answer()


@dp.callback_query_handler(state=TicketCreate.division)
async def division_pick(call: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    # print(f'Состояние в division_pick: {current_state}')
    async with state.proxy() as data:
        data['p_division'] = call.data
        data[f'{current_state.split(":")[1]}'] = current_state.split(':')[1]
    await state.set_state(TicketCreate.confirmation)
    await confirm_pick(call.message.chat.id, call.message.message_id, data["division"], data['p_division'])
    await call.answer()


@dp.callback_query_handler(state=TicketCreate.employee)
async def employee_pick(call: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    async with state.proxy() as data:
        data['p_employee'] = call.data
        data[f'{current_state.split(":")[1]}'] = current_state.split(':')[1]
    await state.set_state(TicketCreate.confirmation)
    await confirm_pick(call.message.chat.id, call.message.message_id, data['employee'], data['p_employee'])
    await call.answer()


@dp.callback_query_handler(state=TicketCreate.request_menu)
async def option_pick(call, state: FSMContext):
    if call.data == "create_req":
        current_state = await state.get_state()
        await show_categories(call, categories)
    elif call.data == "check_status":
        print("SOSAL PIZDU")
