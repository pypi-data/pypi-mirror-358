"""
# File       : apis.py
# Time       ：2024/8/26 下午10:19
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import httpx
from app_tools_zxw.msvc_user_auth.schemas import *
from app_tools_zxw.msvc_user_auth.interface import (InterfaceUserAuth,
                                                    oauth2_scheme, WeChatLoginRequest,
                                                    WeChatQRCodeRequest, TokenRefreshRequest,
                                                    RoleAuthRequest)

# get router from os environment
router = APIRouter(prefix="/user_center", tags=["用户管理"])
interface_user_auth = InterfaceUserAuth("http://127.0.0.1:8101")


@router.post("/account/register", response_model=返回_login)
async def 账号密码_注册(data: 请求_账号密码_注册) -> 返回_login:
    return await interface_user_auth.账号密码_注册(data)


@router.post("/account/login", response_model=返回_login)
async def 账号密码_登录(data: 请求_账号密码_登录):
    return await interface_user_auth.账号密码_登录(data)


@router.post("/account/login-form", response_model=返回_login)
async def 账号密码_登录_Form数据(login_info: OAuth2PasswordRequestForm = Depends()):
    data = 请求_账号密码_登录(username=login_info.username, password=login_info.password)
    return await 账号密码_登录(data)


@router.post("/wechat/get-login-qrcode", response_model=返回_获取_登录二维码URL)
async def 获取_登录二维码URL(request: WeChatQRCodeRequest):
    # 调用用户管理微服务获取微信二维码URL
    # 请求URL DEMO ： http://127.0.0.1:8101/wechat/qr-login/get-qrcode
    return await interface_user_auth.获取_登录二维码URL(request)


@router.post("/wechat/login", response_model=返回_login)
async def 微信登录(request: WeChatLoginRequest):
    return await interface_user_auth.微信登录(request)


@router.post("/token/refresh", response_model=返回_更新Token)
async def 更新Token(request: TokenRefreshRequest, token: str = Depends(oauth2_scheme)):
    return await interface_user_auth.更新Token(request, token)


@router.post("/get-current-user", response_model=Payload)
async def 获取当前用户(token: str = Depends(oauth2_scheme)) -> Payload:
    return await interface_user_auth.获取当前用户(token)


@router.post("/roles/role-auth", response_model=返回_验证角色_from_header)
async def 验证角色_from_header(info: 请求_验证角色_from_header, token: str = Depends(oauth2_scheme)):
    return await interface_user_auth.验证角色_from_header(info, token)


@router.post("/account/send-verification-code", response_model=dict)
async def 发送验证码(phone: str):
    return await interface_user_auth.发送验证码(phone)


@router.post("/account/register-phone", response_model=返回_login)
async def 注册_手机(data: 请求_手机邮箱_注册):
    return await interface_user_auth.注册_手机(data)


@router.post("/account/login-phone", response_model=返回_login)
async def 登录_手机(data: 请求_手机邮箱_登录):
    return await interface_user_auth.登录_手机(data)


@router.post("/account/change-phone", response_model=返回_login)
async def 更换绑定手机号(new_phone: str, sms_code: str, token: str = Depends(oauth2_scheme)):
    return await interface_user_auth.更换绑定手机号(new_phone, sms_code, token)


if __name__ == '__main__':
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware

    app = FastAPI(title="app-tools-zxw 接口-用户微服务")
    app.include_router(router)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
