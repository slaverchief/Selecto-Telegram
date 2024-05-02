from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from states import *
import kb
from api import APIClient
from service import *

basic_router = Router()


@basic_router.message(Command('start'))
@catch_exceptions(False)
async def handler(message: types.Message):
    await get_user(message.from_user.id)
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb.startkb,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )
    await message.answer("Что вы хотите сделать?", reply_markup=keyboard)


@basic_router.message(F.text == "Создать выборку")
@catch_exceptions(True)
async def handler(message: types.Message, state: FSMContext):
    await get_user(message.from_user.id)
    await message.answer("Введите название вашей выборки")
    await state.set_state(Selection.name.state)


@basic_router.message(Selection.name)
@catch_exceptions(True)
async def handler(message: types.Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    res = await APIClient.selection_post(owner=user, name=message.text)
    await message.answer("Выборка создана")
