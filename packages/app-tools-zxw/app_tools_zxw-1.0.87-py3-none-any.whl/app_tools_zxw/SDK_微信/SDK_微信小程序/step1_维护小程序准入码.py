"""
# File       : 获取小程序准入码.py
# Time       ：2024/8/22 08:20
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：获取并自动维护 access token

               注意：此access token与公众号的用户access token有重大区别。
                    本TOKEN主要用于服务器请求其他小程序api。
"""
# from aiohttp_requests import requests as ioRequests
import httpx
import datetime
import asyncio


# 获取并自动维护access token
# 实例化后，用户只需无脑调用get_access_token()即可。
# 在服务启动时，作为全局变量实例化，并调用一次get_access_token()
class AccessTokenTokenMaintenance:
    __getUrl = ''
    __access_token = ''
    __expire_time = datetime.datetime.now() + datetime.timedelta(days=-1)
    __正在请求access_token = False

    def __init__(self, wx_APP_ID, wx_APP_Secret):
        self.__getUrl = 'https://api.weixin.qq.com/cgi-bin/token?' + \
                        f'grant_type=client_credential&appid={wx_APP_ID}&secret={wx_APP_Secret}'

    async def get_access_token(self):
        if self.__expire_time > datetime.datetime.now():
            return self.__access_token
        else:
            print('access token已过期，重新获取中...')
            return await self.__update_accessToken()

    async def __update_accessToken(self):
        # 已有线程正在请求access token
        while self.__正在请求access_token is True:
            await asyncio.sleep(0.5)
        if self.__expire_time > datetime.datetime.now():
            return self.__access_token

        # 请求access_token
        self.__正在请求access_token = True
        async with httpx.AsyncClient() as client:
            response = await client.get(self.__getUrl)
            re = response.json()
        # res = await ioRequests.get(self.__getUrl)
        # re = await res.json()
        print("微信小程序access token = ", re)
        # print("res = ", res)
        #
        if 'expires_in' not in re.keys():
            print('access token 获取失败：', re)
            return None
        #
        expires_in = re['expires_in']
        self.__access_token = re['access_token']
        self.__expire_time = datetime.datetime.now(
        ) + datetime.timedelta(seconds=expires_in)
        #
        self.__正在请求access_token = False
        return self.__access_token
