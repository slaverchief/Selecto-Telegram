from aiogram.fsm.state import StatesGroup, State


class Selection(StatesGroup):
    name = State()
