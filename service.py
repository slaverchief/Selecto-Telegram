from api import APIClient



async def get_user(tgid):
    userid = await APIClient.get_user_by_id(tgid)
    if not userid:
        raise Exception("Вы не имеете доступа к боту")
    return userid
