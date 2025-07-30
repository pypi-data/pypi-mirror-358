# from aiohttp_requests import requests as ioRequests
from typing import Tuple
import httpx
import asyncio
from fastapi import HTTPException, status


# 获取openid
async def get_openid和sessionKey(WX_Login_code, appid_s, secret_s) -> Tuple[str, str]:
    # 整理请求地址
    login_code = WX_Login_code
    if type(WX_Login_code) == bytes:
        login_code = WX_Login_code.decode('utf-8')

    url = 'https://api.weixin.qq.com/sns/jscode2session?appid=' + appid_s + \
          '&secret=' + secret_s + '&js_code=' + \
          login_code + '&grant_type=authorization_code'
    #
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        resDATA = response.json()
    # res = await ioRequests.get(url)
    # resDATA = json.loads(await res.text())

    try_again = 0
    while try_again < 3:
        if 'openid' in resDATA.keys():
            openid = resDATA['openid']
            session_key = resDATA['session_key']
            # res.close()
            # print(openid)
            return openid, session_key
        else:
            print('根据登陆码请求openid失败，重试一次...', resDATA)
            # res.close()
            await asyncio.sleep(1)
            try_again += 1

    # return (None, resDATA)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=resDATA)


if __name__ == '__main__':
    from asyncio import run
    from config import wx_APP_ID, wx_APP_Secret

    code = "081fz9Ha1AzAJD0L38Ja1oZI7e1fz9Hb"
    a = run(get_openid和sessionKey(code, wx_APP_ID, wx_APP_Secret))
    print(a)
