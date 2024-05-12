from aiogram import types, F, Router, MagicFilter
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from states import *
import kb
from api import APIClient
from service import *
from middlwares import CatchExceptions
from data import DEBUG

basic_router = Router()
if not DEBUG:
    basic_router.message.middleware(CatchExceptions())
    basic_router.callback_query.middleware(CatchExceptions(True))


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
    text, builder = await generate_edit_sel_message(selection)
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
    text, builder = await generate_edit_sel_message(selection)
    await message.answer(text=text, reply_markup=builder.as_markup())
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
    text, builder = await generate_edit_sel_message(selection)
    await message.answer(text=text, reply_markup=builder.as_markup())
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
    await callback.message.answer("Введите значимость выбранного варианта для выбранной характеристики")
    await state.set_state(OptionChar.waiting_for_option_value.state)


@basic_router.message(OptionChar.waiting_for_option_value)
async def handler(message: types.Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    data = await state.get_data()
    char = data['char_id']
    selection = data['selection']
    option = data['option_id']
    value = int(message.text)
    await APIClient.option_char_post(char=char, option=option, value=value)
    await message.answer('Выриант выбора сопоставлен с характеристикой')
    text, builder = await generate_edit_sel_message(selection)
    await message.answer(text=text, reply_markup=builder.as_markup())
    await state.clear()


# CREATING CONNECTION

# DELETEANY

@basic_router.callback_query(F.data.contains('pick_to_delete_char_'))
async def handler(callback: types.CallbackQuery, state: FSMContext):
    user = await get_user(callback.from_user.id)
    selection = int(callback.data.split('_')[4])
    builder = InlineKeyboardBuilder()
    chars = await APIClient.char_get(selection=selection)
    for char in chars:
        builder.add(
            types.InlineKeyboardButton(text=char['name'], callback_data=f'delete_char_{char['id']}'))
    await callback.message.answer(text='Выберите удаляемую характеристику',
                                  reply_markup=builder.as_markup())
    await state.update_data(selection=selection)


@basic_router.callback_query(F.data.contains('pick_to_delete_option_'))
async def handler(callback: types.CallbackQuery, state: FSMContext):
    user = await get_user(callback.from_user.id)
    selection = int(callback.data.split('_')[4])
    builder = InlineKeyboardBuilder()
    options = await APIClient.option_get(selection=selection)
    for option in options:
        builder.add(
            types.InlineKeyboardButton(text=option['name'], callback_data=f'delete_option_{option['id']}'))
    await callback.message.answer(text='Выберите удаляемый вариант выбора',
                                  reply_markup=builder.as_markup())
    await state.update_data(selection=selection)


@basic_router.callback_query(F.data.contains('delete_char'))
async def handler(callback: types.CallbackQuery, state: FSMContext):
    user = await get_user(callback.from_user.id)
    await APIClient.char_delete(id=int(callback.data.split('_')[2]))
    await callback.message.answer("Характеристика удалена")
    data = await state.get_data()
    selection = data['selection']
    text, builder = await generate_edit_sel_message(selection)
    await callback.message.answer(text=text, reply_markup=builder.as_markup())
    await state.clear()


@basic_router.callback_query(F.data.contains('delete_option'))
async def handler(callback: types.CallbackQuery, state: FSMContext):
    user = await get_user(callback.from_user.id)
    await APIClient.option_delete(id=int(callback.data.split('_')[2]))
    await callback.message.answer("Вариант выбора удален")
    data = await state.get_data()
    selection = data['selection']
    text, builder = await generate_edit_sel_message(selection)
    await callback.message.answer(text=text, reply_markup=builder.as_markup())
    await state.clear()

# DELETEANY

# EXECUTE SELECTION


@basic_router.message(F.text == "Произвести выборку")
async def handler(message: types.Message):
    await get_user(message.from_user.id)
    builder = InlineKeyboardBuilder()
    selections = await APIClient.selection_get()
    for selection in selections:
        builder.add(types.InlineKeyboardButton(text=selection['name'],
                                               callback_data=f'execute_{selection['id']}'))
    await message.answer(text='Выберите производящуюся выборку', reply_markup=builder.as_markup())


@basic_router.callback_query(F.data.contains('execute_'))
async def handler(callback: types.CallbackQuery):
    await get_user(callback.from_user.id)
    selection = int(callback.data.split('_')[1])
    res = await APIClient.calc(selection=selection)
    await callback.message.answer(text=f'Самый оптимальный вариант - {res}')

# EXECUTE SELECTION



