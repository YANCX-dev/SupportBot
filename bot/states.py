from aiogram.dispatcher.filters.state import StatesGroup, State


class TicketCreate(StatesGroup):
    start = State()
    division = State()
    employee = State()
    request_menu = State()
    category = State()
    description = State()
    confirmation = State()
