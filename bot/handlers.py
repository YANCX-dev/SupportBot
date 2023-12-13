from aiogram import types
from aiogram.dispatcher import FSMContext
from .states import StateMachine
from . import bot, dp
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

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
                       'СВК-3',
                       'Лаборатория',
                       'Березовка',
                       'Шумаково']  # Временные подразделения
names: list[str] = ['Ольга', 'Ирина', 'Елена']
options = [
    {"text": "Создать обращение", "callback_data": "create_req"},
    {"text": "Проверить статус", "callback_data": "check_status"}
]
categories = [
    {"text": "1С:Селекция", "callback_data": "1С:Селекция"},
    {"text": "1С:УПП", "callback_data": "1С:УПП"},
    {"text": "Моб приложение Ariant Pig", "callback_data": "Моб приложение Ariant Pig"},
    {"text": "Интернет, связь", "callback_data": "Интернет, связь"},
    {"text": "Оборудование", "callback_data": "Оборудование"},
    {"text": "Моб Агроном", "callback_data": "Моб Агроном"},
    {"text": "Назад", "callback_data": "categories_back"}
]
servises = [
    {"text": "Тестовая услуга", "callback_data": "Тестовая услуга"},
    {"text": "Тестовая услуга 1", "callback_data": "Тестовая услуга1"}
]


# TODO: TicketCreate rename to StateMachine

@dp.callback_query_handler(state=StateMachine.confirmation)
async def confirm_choice(call: types.CallbackQuery, state: FSMContext):
    print(f'CONFiRM_CHOICE CALL {call.data}')
    async with state.proxy() as data:
        if call.data == "division_confirm_yes":
            await bot.edit_message_text(f"Выбранное подразделение: <b>{data['p_division']}</b>", call.message.chat.id,
                                        call.message.message_id, parse_mode='HTML')
            await state.set_state(StateMachine.employee)
            await show_employee(call, names)
            await call.answer()

        elif call.data == "division_confirm_no":
            await state.set_state(StateMachine.division)
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            await show_division(call, division)

        elif call.data == "employee_confirm_yes":
            await state.set_state(StateMachine.request_menu)
            cs = await state.get_state()
            print(f'STATE {cs}')
            await bot.edit_message_text(f'Сотрудник: <b>{data["p_employee"]}</b>', call.message.chat.id,
                                        call.message.message_id, parse_mode='HTML')
            await display_options(call, options)
            await call.answer()

        elif call.data == "employee_confirm_no":
            await state.set_state(StateMachine.employee)
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            await show_employee(call, names)
            await call.answer()

        elif call.data == "service_confirm_yes":
            await state.set_state(StateMachine.description)
            await bot.edit_message_text(f'Выбранная услуга: <b>{data["p_service"]}</b>', call.message.chat.id,
                                        call.message.message_id, parse_mode='HTML')
            await show_description(call)
            await call.answer()

        elif call.data == "service_confirm_no":
            await state.set_state(StateMachine.service)
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            await show_services(call, servises)
            await call.answer()

        elif call.data == "category_confirm_yes":
            await state.set_state(StateMachine.service)
            await bot.edit_message_text(f'Выбранная категория: <b>{data["p_category"]}</b>', call.message.chat.id,
                                        call.message.message_id, parse_mode='HTML')
            await show_services(call, servises)
            await call.answer()

        elif call.data == "category_confirm_no":
            await state.set_state(StateMachine.category)
            await show_categories(call, categories)
            await call.answer()

        elif call.data == "descr_yes":
            await bot.edit_message_text(f'Описание: <b>{data["p_description"]}</b>', call.message.chat.id,
                                        call.message.message_id, parse_mode='HTML')
            await state.set_state(StateMachine.image)
            await show_images(call, state)
            await call.answer()

        elif call.data == "descr_no":
            await state.set_state(StateMachine.description)
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            await show_description(call)
            await call.answer()

        elif call.data == "image_next":
            await show_ticket_info(call, state)
            await create_new_ticket(call, state)
            await call.answer()

        elif call.data == "create_new_ticket":
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            await state.set_state(StateMachine.division)
            await show_division(call, division)


async def create_buttons(item_array):
    keyboard = InlineKeyboardMarkup(row_width=3)
    for item in item_array:
        cd = item
        btn = InlineKeyboardButton(text=item, callback_data=cd)
        keyboard.add(btn)
    return keyboard


async def create_new_ticket(call, state: FSMContext):
    kb = InlineKeyboardMarkup(row_width=3)
    btn = InlineKeyboardButton("Да", callback_data="create_new_ticket")
    kb.add(btn)
    await state.set_state(StateMachine.confirmation)
    await bot.send_message(call.message.chat.id, "Создать новую заявку?", reply_markup=kb)


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


async def show_categories(call, category_list):
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    kb = await create_keyboard(category_list)

    await bot.send_message(call.message.chat.id, "Выберите категорию:",
                           reply_markup=kb)


async def display_options(call, option_btn_list):
    keyboard = await create_keyboard(option_btn_list)
    await bot.send_message(call.message.chat.id, "Выберите действие:",
                           reply_markup=keyboard)


async def show_services(call, service_list):
    # await bot.delete_message(call.message.chat.id, call.message.message_id)
    kb = await create_keyboard(service_list)
    await bot.send_message(call.message.chat.id, "Выберите услугу",
                           reply_markup=kb)


async def show_description(call):
    await bot.send_message(call.message.chat.id, "Опишите проблему (напишите в чат):")


async def show_images(call, state):
    kb = InlineKeyboardMarkup()
    next_btn = InlineKeyboardButton("Пропустить", callback_data="image_next")
    kb.add(next_btn)
    await state.set_state(StateMachine.confirmation)
    await bot.send_message(call.message.chat.id, "Отправьте изображение ошибки (Если есть)",
                           reply_markup=kb)


async def confirm_pick(chat_id, message_id, data_state, data):
    btn1 = InlineKeyboardButton(text="Да", callback_data=f'{data_state}_confirm_yes')
    btn2 = InlineKeyboardButton(text="Нет", callback_data=f'{data_state}_confirm_no')
    kb = InlineKeyboardMarkup()
    kb.add(btn1, btn2)
    await bot.delete_message(chat_id, message_id)
    await bot.send_message(chat_id, f'Подтвердить выбор: {data} ?', reply_markup=kb)


async def confirm_descr(chat_id, state: FSMContext):
    async with state.proxy() as data:
        btn1 = InlineKeyboardButton(text="Да", callback_data=f'descr_yes')
        btn2 = InlineKeyboardButton(text="Нет", callback_data=f'descr_no')
        kb1 = InlineKeyboardMarkup()
        kb1.add(btn1, btn2)
        await state.set_state(StateMachine.confirmation)
        await bot.send_message(chat_id, "Подтвердить описание ?\n" + data['p_description'], parse_mode="HTML",
                               reply_markup=kb1)


async def show_ticket_info(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        await bot.edit_message_text(
            f'Заявка:\n Подразделение: {data["p_division"]}\n Сотрудник: {data["p_employee"]}\n Категория: {data["p_category"]}\n Услуга: {data["p_service"]}\n Описание: {data["p_description"]}\n <b>Сформирована!</b>',
            call.message.chat.id, call.message.message_id, parse_mode="HTML")


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

    await StateMachine.next()


@dp.callback_query_handler(text='start_yes', state=StateMachine.start)
async def start_callback(callback: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    # current_state = await state.get_state()
    # print(f'Состояние в start_callback: {current_state}')
    await StateMachine.next()
    await show_division(callback, division)
    await callback.answer()


@dp.callback_query_handler(state=StateMachine.division)
async def division_pick(call: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    # print(f'Состояние в division_pick: {current_state}')
    async with state.proxy() as data:
        data['p_division'] = call.data
        data[f'{current_state.split(":")[1]}'] = current_state.split(':')[1]
    await state.set_state(StateMachine.confirmation)
    await confirm_pick(call.message.chat.id, call.message.message_id, data["division"], data['p_division'])
    await call.answer()


@dp.callback_query_handler(state=StateMachine.employee)
async def employee_pick(call: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    async with state.proxy() as data:
        data['p_employee'] = call.data
        data[f'{current_state.split(":")[1]}'] = current_state.split(':')[1]
    await state.set_state(StateMachine.confirmation)
    await confirm_pick(call.message.chat.id, call.message.message_id, data['employee'], data['p_employee'])
    await call.answer()


@dp.callback_query_handler(state=StateMachine.request_menu)
async def option_pick(call: types.CallbackQuery, state: FSMContext):
    if call.data == "create_req":
        current_state = await state.get_state()
        await show_categories(call, categories)
        await state.set_state(StateMachine.category)

    # elif call.data == "check_status":


@dp.callback_query_handler(state=StateMachine.category)
async def category_pick(call: types.CallbackQuery, state: FSMContext):
    if call.data == "categories_back":
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await display_options(call, options)
        await state.set_state(StateMachine.request_menu)
    elif call.data != "categories_back":
        current_state = await state.get_state()
        async with state.proxy() as data:
            data["p_category"] = call.data
            data[f'{current_state.split(":")[1]}'] = current_state.split(':')[1]
        await state.set_state(StateMachine.confirmation)
        await confirm_pick(call.message.chat.id, call.message.message_id, data['category'], data['p_category'])
        await call.answer()


@dp.callback_query_handler(state=StateMachine.service)
async def service_pick(call: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    async with state.proxy() as data:
        data['p_service'] = call.data
        data[f'{current_state.split(":")[1]}'] = current_state.split(':')[1]
    await state.set_state(StateMachine.confirmation)
    await confirm_pick(call.message.chat.id, call.message.message_id, data['service'], data['p_service'])


@dp.message_handler(state=StateMachine.description)
async def get_description(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    async with state.proxy() as data:
        data['p_description'] = message.text
        data[f'{current_state.split(":")[1]}'] = current_state.split(':')[1]
    await confirm_descr(message.chat.id, state)

# # Обработчик для получения изображений
# @dp.message_handler(state=StateMachine.image,content_types=ContentType.PHOTO)
# async def handle_images(message: types.Message):
#     # Получение информации о картинке
#     photo = message.photo[-1]  # Берем последнюю (самую большую) версию изображения
#     file_id = photo.file_id
#     # Получение объекта файла
#     file = await bot.get_file(file_id)
#     # Загрузка файла
#     photo_file = await file.download()
#     # Дальнейшая обработка изображения
#
