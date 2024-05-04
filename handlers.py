from aiogram import types, F, Router, MagicFilter
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from states import *
import kb
from api import APIClient
from service import *
from middlwares import CatchExceptions

basic_router = Router()
basic_router.message.middleware(CatchExceptions())


@basic_router.message(Command('start'))
async def handler(message: types.Message):
    await get_user(message.from_user.id)
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb.startkb,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )
    await message.answer("Что вы хотите сделать?", reply_markup=keyboard)


@basic_router.message(F.text == "Создать выборку")
async def handler(message: types.Message, state: FSMContext):
    await get_user(message.from_user.id)
    await message.answer("Введите название вашей выборки")
    await state.set_state(Selection.waiting_for_name.state)


@basic_router.message(Selection.waiting_for_name)
async def handler(message: types.Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    res = await APIClient.selection_post(owner=user, name=message.text)
    await message.answer("Выборка создана")
    await state.clear()


@basic_router.message(F.text == "Редактировать выборку")
async def handler(message: types.Message):
    user = await get_user(message.from_user.id)
    builder = InlineKeyboardBuilder()
    selections = await APIClient.selection_get(owner=user)
    for json in selections.get('result'):
        builder.add(types.InlineKeyboardButton(
            text=json.get('name'),
            callback_data=f'selection_{json.get('id')}')
        )
    await message.answer(
        "Выберите выборку, которую вы хотите редактировать",
        reply_markup=builder.as_markup()
    )


@basic_router.callback_query(F.data.contains('selection_'))
async def handler(callback: types.CallbackQuery):
    user = await get_user(callback.from_user.id)
