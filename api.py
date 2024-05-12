from data import ACCESS_TOKEN, HOST
import aiohttp
from exceptions import APIException


class APIClient:
    __host = HOST+'api/'
    __headers = {'AccessToken': ACCESS_TOKEN}

    @staticmethod
    async def __base_post(extra_url, **kwargs):
        url = APIClient.__host + extra_url
        session = aiohttp.ClientSession(headers=APIClient.__headers)
        resp = await session.post(json=kwargs, url=url)
        res = await resp.json()
        if res['status'] == 'fail':
            await session.close()
            raise APIException("Произошла какая-то ошибка. Возможно неверно введены данные")
        elif res['status'] != 'success':
            await session.close()
            raise APIException("Невалидный статус ответа от сервера")
        await session.close()
        try:
            return res['result']
        except KeyError:
            pass

    @staticmethod
    async def __base_get(extra_url, **kwargs):
        url = APIClient.__host + extra_url
        session = aiohttp.ClientSession(headers=APIClient.__headers)
        resp = await session.get(json=kwargs, url=url)
        res = await resp.json()
        if res['status'] == 'fail':
            await session.close()
            raise APIException("Произошла какая-то ошибка. Возможно неверно введены данные")
        elif res['status'] != 'success':
            await session.close()
            raise APIException("Невалидный статус ответа от сервера")
        await session.close()
        try:
            return res['result']
        except KeyError:
            pass

    @staticmethod
    async def __base_delete(extra_url, **kwargs):
        url = APIClient.__host + extra_url
        session = aiohttp.ClientSession(headers=APIClient.__headers)
        resp = await session.delete(json=kwargs, url=url)
        res = await resp.json()
        if res['status'] == 'fail':
            await session.close()
            raise APIException("Произошла какая-то ошибка. Возможно неверно введены данные")
        elif res['status'] != 'success':
            await session.close()
            raise APIException("Невалидный статус ответа от сервера")
        await session.close()
        try:
            return res['result']
        except KeyError:
            pass

    @staticmethod
    def extend_headers(extra_headers: dict):
        APIClient.__headers = APIClient.__headers | extra_headers

    @staticmethod
    async def get_user_by_id(tgid):
        url = APIClient.__host + 'user'
        session = aiohttp.ClientSession(headers=APIClient.__headers)
        resp = await session.get(json={'auth_id': tgid}, url=url)
        res = await resp.json()
        user = None
        if not res['status'] == 'success':
            raise APIException("Невалидный статус ответа от сервера")
        else:
            user = res['result'].get('id', None)
        await session.close()
        return user

    @staticmethod
    async def selection_get(**kwargs):
        return await APIClient.__base_get('selection', **kwargs)

    @staticmethod
    async def selection_post(**kwargs):
        return await APIClient.__base_post('selection', **kwargs)

    @staticmethod
    async def option_get(**kwargs):
        return await APIClient.__base_get('option', **kwargs)

    @staticmethod
    async def option_post(**kwargs):
        return await APIClient.__base_post('option', **kwargs)

    @staticmethod
    async def option_delete(**kwargs):
        return await APIClient.__base_delete('option', **kwargs)

    @staticmethod
    async def char_get(**kwargs):
        return await APIClient.__base_get('char', **kwargs)

    @staticmethod
    async def char_post(**kwargs):
        return await APIClient.__base_post('char', **kwargs)

    @staticmethod
    async def char_delete(**kwargs):
        return await APIClient.__base_delete('char', **kwargs)

    @staticmethod
    async def option_char_get(**kwargs):
        return await APIClient.__base_get('optionchar', **kwargs)

    @staticmethod
    async def option_char_post(**kwargs):
        return await APIClient.__base_post('optionchar', **kwargs)

    @staticmethod
    async def calc(**kwargs):
        return await APIClient.__base_get('calc', **kwargs)
