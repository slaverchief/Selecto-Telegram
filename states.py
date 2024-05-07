from aiogram.fsm.state import StatesGroup, State


class Selection(StatesGroup):
    waiting_for_name = State()

class Char(StatesGroup):
    waiting_for_char_name = State()
    waiting_for_char_priority = State()

