from data import  HOST
import aiohttp
from exceptions import APIException


class APIClient:
    __host = HOST+'api/'
    headers = {}

    @staticmethod
    async def __send_request(kwargs, url, session, request_method):
        resp = await request_method(json=kwargs, url=url)
        res = await APIClient.__status_check(resp, session)
        await session.close()
        return res.get('result')


    @staticmethod
    async def __status_check(resp, session):
        json = await resp.json()
        if resp.status != 200:
            detail = json.get('detail')
            if detail:
                raise APIException(f"Ошибка: {detail}")
            raise APIException(f'Произошла непредвиденная ошибка')
        return json

    @staticmethod
    async def __base_post(extra_url, **kwargs):
        url = APIClient.__host + extra_url
        session = aiohttp.ClientSession(headers=APIClient.headers)
        request_res = await APIClient.__send_request(kwargs, url, session, session.post)
        return request_res

    @staticmethod
    async def __base_get(extra_url, **kwargs):
        url = APIClient.__host + extra_url
        session = aiohttp.ClientSession(headers=APIClient.headers)
        request_res = await APIClient.__send_request(kwargs, url, session, session.get)
        return request_res

    @staticmethod
    async def __base_delete(extra_url, **kwargs):
        url = APIClient.__host + extra_url
        session = aiohttp.ClientSession(headers=APIClient.headers)
        request_res = await APIClient.__send_request(kwargs, url, session, session.delete)
        return request_res

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
