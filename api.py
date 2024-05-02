from data import ACCESS_TOKEN, HOST
import aiohttp
from exceptions import APIException


class APIClient:
    __host = HOST+'api/'
    __headers = {'AccessToken': ACCESS_TOKEN}

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
        url = APIClient.__host + 'selection'
        session = aiohttp.ClientSession(headers=APIClient.__headers)
        resp = await session.get(json=kwargs, url=url)
        res = await resp.json()
        if not res['status'] == 'success':
            raise APIException("Невалидный статус ответа от сервера")
        return res

    async def selection_post(**kwargs):
        url = APIClient.__host + 'selection'
        session = aiohttp.ClientSession(headers=APIClient.__headers)
        resp = await session.post(json=kwargs, url=url)
        res = await resp.json()
        if not res['status'] == 'success':
            raise APIException("Невалидный статус ответа от сервера")