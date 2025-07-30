"""
# File       : 获取_openid和accessToken.py
# Time       ：2024/8/22 08:12
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
import httpx
from app_tools_zxw.Errors.api_errors import HTTPException_AppToolsSZXW


async def get_access_token_and_openid_async(code: str, app_id: str, app_secret: str) -> (str, str):
    """
    :param code: 前端获取的code
    :param app_id: 微信公众号的app_id
    :param app_secret: 微信公众号的app_secret
    :return:
    """
    url = f"https://api.weixin.qq.com/sns/oauth2/access_token?appid={app_id}&secret={app_secret}&code={code}&grant_type=authorization_code"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        token_data = response.json()

        if "errcode" in token_data:
            raise HTTPException_AppToolsSZXW(error_code=1015,
                                             http_status_code=400,
                                             detail=f"Failed to get access_token: {token_data['errmsg']}")

        access_token = token_data.get("access_token")
        openid = token_data.get("openid")
        return access_token, openid
