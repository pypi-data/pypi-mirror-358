"""
# File       : api_用户信息.py
# Time       ：2024/8/22 09:16
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from fastapi import APIRouter, HTTPException
from app_tools_zxw.Errors.api_errors import HTTPException_AppToolsSZXW
from app_tools_zxw.SDK_微信.SDK_微信公众号或网站应用.获取_openid和access_token import get_access_token_and_openid_async

router = APIRouter(prefix="/wechat_pub/v1", tags=["微信公众号"])


@router.get("/login")
async def login(code: str):
    try:
        access_token, openid = await get_access_token_and_openid_async(code)
        return {
            "status": "success",
            "access_token": access_token,
            "openid": openid
        }
    except Exception as e:
        raise HTTPException_AppToolsSZXW(error_code=1015,
                                         http_status_code=500,
                                         detail=str(e))
