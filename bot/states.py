from aiogram.dispatcher.filters.state import StatesGroup, State


class TicketCreate(StatesGroup):
    start = State()
    division = State()
    full_name = State()
    category = State()
    description = State()
    confirmation = State()
