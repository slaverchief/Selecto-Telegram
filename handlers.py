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
# basic_router.message.middleware(CatchExceptions())


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
    if not selections:
        raise Exception("У вас нет ни одной выборки, создайте хотя бы одну")
    for json in selections:
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
    selection = int(callback.data.split('_')[1])
    builder = InlineKeyboardBuilder()
    buttons = (types.InlineKeyboardButton(text='Создать характеристику', callback_data=f'create_char_{selection}'),
               types.InlineKeyboardButton(text='Создать вариант выбора', callback_data=f'create_option_{selection}'),
               types.InlineKeyboardButton(text='Сопоставить вариант выбора и характеристику',
                                          callback_data=f'create_optionchar_{selection}'),
               types.InlineKeyboardButton(text='Удалить характеристику', callback_data=f'edit_char_{selection}'),
               types.InlineKeyboardButton(text='Удалить вариант выбора', callback_data=f'edit_option_{selection}'),
               )
    for button in buttons:
        builder.add(button)
    text = ''
    chars = await APIClient.char_get(selection=selection)
    optionchars = await APIClient.option_char_get(selection=selection)
    for char in chars:
        text += f'Характеристика {char.get('name')} с приоритетом {char.get('priority')}\n'
    text += '<-------------->\n'
    for optionchar in optionchars:
        text += (f'Вариант выбора {optionchar.get('option')} со значимостью {optionchar.get('value')} '
                 f'к характеристике {optionchar.get('char')}\n')
    await callback.message.answer(text=text, reply_markup=builder.as_markup())


# CREATING CHAR

@basic_router.callback_query(F.data.contains('create_char_'))
async def handler(callback: types.CallbackQuery, state: FSMContext):
    user = await get_user(callback.from_user.id)
    selection = int(callback.data.split('_')[2])
    await state.update_data(selection=selection)
    await callback.message.answer('Введите название характеристики')
    await state.set_state(Char.waiting_for_char_name.state)


@basic_router.message(Char.waiting_for_char_name)
async def handler(message: types.Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    await state.update_data(name=message.text)
    await message.answer('Введите приоритет характеристики')
    await state.set_state(Char.waiting_for_char_priority.state)


@basic_router.message(Char.waiting_for_char_priority)
async def handler(message: types.Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    data = await state.get_data()
    selection = data.get('selection')
    name = data.get('name')
    priority = int(message.text)
    await APIClient.char_post(selection=selection, name=name, priority=priority)
    await message.answer("Характеристика создана")
    await state.clear()

# CREATING CHAR

# CREATING OPTION


@basic_router.callback_query(F.data.contains('create_option_'))
async def handler(callback: types.CallbackQuery, state: FSMContext):
    user = await get_user(callback.from_user.id)
    selection = int(callback.data.split('_')[2])
    await state.update_data(selection=selection)
    await callback.message.answer('Введите название варианта выбора')
    await state.set_state(Option.waiting_for_option_name.state)


@basic_router.message(Option.waiting_for_option_name)
async def handler(message: types.Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    data = await state.get_data()
    selection = data.get('selection')
    name = message.text
    option = await APIClient.option_post(selection=selection, name=name)
    await message.answer("Вариант выбора создан")
    await state.clear()

# CREATING OPTION

# CREATING CONNECTION


@basic_router.callback_query(F.data.contains('create_optionchar_'))
async def handler(callback: types.CallbackQuery, state: FSMContext):
    user = await get_user(callback.from_user.id)
    selection = int(callback.data.split('_')[2])
    builder = InlineKeyboardBuilder()
    chars = await APIClient.char_get(selection=selection)
    for char in chars:
        builder.add(types.InlineKeyboardButton(text=char['name'], callback_data=f'pick_char_connection_{char['id']}'))
    await state.update_data(selection=selection)
    await callback.message.answer(text='Выберите характеристику, с которой сопоставляете вариант выбора',
                         reply_markup=builder.as_markup())


@basic_router.callback_query(F.data.contains('pick_char_connection_'))
async def handler(callback: types.CallbackQuery, state: FSMContext):
    user = await get_user(callback.from_user.id)
    await state.update_data(char_id=int(callback.data.split('_')[3]))
    data = await state.get_data()
    selection = data['selection']
    builder = InlineKeyboardBuilder()
    options = await APIClient.option_get(selection=selection)
    for option in options:
        builder.add(types.InlineKeyboardButton(text=option['name'], callback_data=f'pick_option_connection_{option['id']}'))
    await callback.message.answer(text='Выберите сопоставляемый вариант выбора',
                                  reply_markup=builder.as_markup())
    await state.set_state(OptionChar.waiting_for_option_value.state)

@basic_router.callback_query(F.data.contains('pick_option_connection_'))
async def handler(callback: types.CallbackQuery, state: FSMContext):
    user = await get_user(callback.from_user.id)
    await state.update_data(option_id=int(callback.data.split('_')[3]))
    await callback.message.answer("Введите значимость выбранного варианта для вырбранной характеристики")
    await state.set_state(OptionChar.waiting_for_option_value.state)


@basic_router.message(OptionChar.waiting_for_option_value)
async def handler(message: types.Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    data = await state.get_data()
    char = data['char_id']
    option = data['option_id']
    value = int(message.text)
    await APIClient.option_char_post(char=char, option=option, value=value)
    await message.answer('Выриант выбора сопоставлен с характеристикой')
    await state.clear()


# CREATING CONNECTION



