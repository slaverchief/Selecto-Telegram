from aiogram import types

# urlkb = InlineKeyboardMarkup(inline_keyboard= [
#         [InlineKeyboardButton(text='Официальная часть', callback_data='v1')],
#         [InlineKeyboardButton(text='Мастер-классы', callback_data='v2')],
# ], resize_keyboard = True)

startkb = [
        [types.KeyboardButton(text="Создать выборку")],
        [types.KeyboardButton(text="Редактировать выборку")],
        [types.KeyboardButton(text="Произвести выборку")],
]


