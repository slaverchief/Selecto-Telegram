from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from exceptions import APIException


class CatchExceptions(BaseMiddleware):
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
            string = f'Проблема при отправлении запроса на сервер: {str(exc)}'
        except Exception as exc:
            string = str(exc)
        await event.answer(string)
