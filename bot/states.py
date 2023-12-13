from aiogram.dispatcher.filters.state import StatesGroup, State


class StateMachine(StatesGroup):
    start = State()
    division = State()
    employee = State()
    request_menu = State()
    category = State()
    service = State()
    description = State()
    image = State()
    confirmation = State()
