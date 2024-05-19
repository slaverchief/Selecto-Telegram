from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from data import DEBUG
from exceptions import APIException


class CatchExceptions(BaseMiddleware):

    def __init__(self, is_callback=False):
        self.callback = is_callback
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        string = ''
        try:
            result = await handler(event, data)
            return result
        except APIException as exc:
            string = f'Проблема при обработке запроса сервером: {str(exc)}'
        except Exception as exc:
            string = "Произошла непредвиденная ошибка"
        if self.callback:
            await event.message.answer(string)
        else:
            await event.answer(string)
