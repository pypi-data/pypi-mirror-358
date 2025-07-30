"""
# File       : api_登录二维码.py
# Time       ：2024/8/21 下午4:17
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app_tools_zxw.SDK_微信.SDK_微信公众号或网站应用.获取_登录二维码URL import get_qrcode_url

router = APIRouter(prefix="/wechat_pub/v1", tags=["微信公众号"])

# 微信登录相关配置
WECHAT_REDIRECT_URI = 'http://192.168.10.102:8080/index'  # 与网页授权获取用户信息里的回调域名一致
WECHAT_SCOPE = 'snsapi_login'  # 'snsapi_login' or 'snsapi_base' ， 扫描二维码必须是snsapi_login
WECHAT_STATE = 'your_custom_state'  # 用于防止CSRF


class QRCodeResponse(BaseModel):
    qr_code_url: str


@router.get("/wechat_login_qr_code", response_model=QRCodeResponse)
async def get_wechat_qr_code():
    try:
        qrcode_url = get_qrcode_url(WECHAT_REDIRECT_URI, WECHAT_SCOPE)
        return QRCodeResponse(qr_code_url=qrcode_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate WeChat QR code URL")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(router, host="0.0.0.0", port=8000)
