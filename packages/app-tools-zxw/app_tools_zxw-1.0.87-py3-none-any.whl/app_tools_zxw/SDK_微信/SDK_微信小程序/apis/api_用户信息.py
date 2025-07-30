"""
# File       : api_用户信息.py
# Time       ：2024/8/22 09:55
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app_tools_zxw.SDK_微信.SDK_微信小程序.获取_openid和sessionKey import get_openid和sessionKey
from app_tools_zxw.SDK_微信.SDK_微信小程序.解密_用户信息 import DecryptData
from config import WeChatMini

router = APIRouter(prefix="/wechat_mini", tags=["微信小程序"])


class WeChatLoginRequest(BaseModel):
    code: str
    encryptedData: str
    iv: str


@router.post("/verify-wechat-user/")
async def 验证_微信用户(data: WeChatLoginRequest):
    # 1. 使用code换取session_key和openid
    openid, session_key = get_openid和sessionKey(data.code, WeChatMini.app_id, WeChatMini.app_secret)

    # 2. 解密用户信息
    try:
        decrypted_data = DecryptData(data.encryptedData, data.iv, session_key)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to decrypt data")

    # 3. 验证解密后的数据是否真实
    # 可以根据需要添加更多的验证逻辑，比如检查解密数据的openid与session_data中的openid是否一致
    if decrypted_data.get_appid() != WeChatMini.app_id:
        raise HTTPException(status_code=400, detail="Data verification failed: appid does not match")

    return {
        "status": "success",
        "decrypted_data": decrypted_data.get_解密后数据()
    }
