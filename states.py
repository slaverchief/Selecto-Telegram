from aiogram.fsm.state import StatesGroup, State


class Selection(StatesGroup):
    waiting_for_name = State()

