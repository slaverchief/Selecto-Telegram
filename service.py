from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
from api import APIClient


async def get_user(tgid):
    userid = await APIClient.get_user_by_id(tgid)
    if not userid:
        raise Exception("Вы не имеете доступа к боту")
    return userid


async def generate_edit_sel_message(selection):
    builder = InlineKeyboardBuilder()
    buttons = (types.InlineKeyboardButton(text='Создать характеристику', callback_data=f'create_char_{selection}'),
               types.InlineKeyboardButton(text='Создать вариант выбора', callback_data=f'create_option_{selection}'),
               types.InlineKeyboardButton(text='Сопоставить вариант выбора и характеристику',
                                          callback_data=f'create_optionchar_{selection}'),
               types.InlineKeyboardButton(text='Удалить характеристику',
                                          callback_data=f'pick_to_delete_char_{selection}'),
               types.InlineKeyboardButton(text='Удалить вариант выбора',
                                          callback_data=f'pick_to_delete_option_{selection}'),
               )
    for button in buttons:
        builder.add(button)
    text = ''
    chars = await APIClient.char_get(selection=selection)
    options = await APIClient.option_get(selection=selection)
    optionchars = await APIClient.option_char_get(selection=selection)
    for char in chars:
        text += f'Характеристика {char.get('name')} с приоритетом {char.get('priority')}\n'
    text += '<-------------->\n'
    for option in options:
        text += f'Вариант выбора с названием {option.get('name')}\n'
    text += '<-------------->\n'
    for optionchar in optionchars:
        text += (f'Вариант выбора {optionchar.get('option')} со значимостью {optionchar.get('value')} '
                 f'к характеристике {optionchar.get('char')}\n')
    return text, builder
