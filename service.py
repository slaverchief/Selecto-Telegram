from api import APIClient
from exceptions import *


def catch_exceptions(is_state: bool):
    def wrap(func):
        async def called(*args, **kwargs):
            message = args[0]
            try:
                kwargs_to_give = {}
                if is_state:
                    kwargs_to_give['state'] = kwargs['state']
                return await func(*args, **kwargs_to_give)
            except APIException as exc:
                await message.answer(f'Проблема при отправлении запроса на сервер: {str(exc)}')
        return called
    return wrap


async def get_user(tgid):
    userid = await APIClient.get_user_by_id(tgid)
    if not userid:
        raise Exception("Вы не имеете доступа к боту")
    return userid
