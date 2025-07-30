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

# OAuth2PasswordBearer 实例
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user_center/account/login-form/")


# Pydantic 模型
class WeChatQRCodeRequest(BaseModel):
    WECHAT_REDIRECT_URI: str


class WeChatLoginRequest(BaseModel):
    code: str
    app_name: str


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class RoleAuthRequest(BaseModel):
    role_name: str
    app_name: str


class InterfaceUserAuth:
    def __init__(self, svc_user: str = "http://127.0.0.1:8101"):
        self.svc_user = svc_user

    async def 账号密码_注册(self, data: 请求_账号密码_注册) -> 返回_login:
        # 调用用户管理微服务进行普通注册
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.svc_user}/api/account/register/",
                json=data.model_dump()
            )
            if response.status_code != 200:
                if response.json().get("detail", None) is not None:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=response.json().get("detail"))
                else:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=response.json() if response.content else "Failed to register")
            return response.json()

    async def 账号密码_登录(self, data: 请求_账号密码_登录) -> 返回_login:
        # 调用用户管理微服务进行普通登录
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.svc_user}/api/account/login/",
                json=data.model_dump()
            )
            if response.status_code != 200:
                if response.json().get("detail", None) is not None:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=response.json().get("detail"))
                else:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=response.json() if response.content else "Failed to login")
            return response.json()

    async def 获取_登录二维码URL(self, request: WeChatQRCodeRequest) -> 返回_获取_登录二维码URL:
        # 调用用户管理微服务获取微信二维码URL
        # 请求URL DEMO ： http://127.0.0.1:8101/wechat/qr-login/get-qrcode
        print({"WECHAT_REDIRECT_URI": request.WECHAT_REDIRECT_URI})
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.svc_user}/wechat/qr-login/get-qrcode",
                json={"WECHAT_REDIRECT_URI": request.WECHAT_REDIRECT_URI}
            )
            if response.status_code != 200:
                if response.json().get("detail", None) is not None:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=response.json().get("detail"))
                else:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=response.json() if response.content else "Failed to get QR code")
            return response.json()

    async def 微信登录(self, request: WeChatLoginRequest) -> 返回_login:
        # 调用用户管理微服务进行微信登录
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.svc_user}/wechat/qr-login/login/",
                params={"code": request.code, "app_name": request.app_name}
            )
            if response.status_code != 200:
                if response.json().get("detail", None) is not None:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=response.json().get("detail"))
                else:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=response.json() if response.content else "Failed to login with WeChat")
            return response.json()

    async def 更新Token(self, request: TokenRefreshRequest, token: str = Depends(oauth2_scheme)) -> 返回_更新Token:
        # 调用用户管理微服务刷新Token
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.svc_user}/api/token/refresh-token/",
                json={"refresh_token": request.refresh_token},
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code != 200:
                if response.json().get("detail", None) is not None:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=response.json().get("detail"))
                else:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=response.json() if response.content else "Failed to refresh token")
            return response.json()

    async def 获取当前用户(self, token: str = Depends(oauth2_scheme)) -> Payload:
        # 将请求头中的Token传递给用户管理微服务
        if not token:
            raise HTTPException(
                status_code=401,
                detail="Failed to get current user")

        # header
        header = {"Authorization": f"Bearer {token}"}
        print(header)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.svc_user}/api/token/get-current-user/",
                headers=header
            )

        if response.status_code != 200:
            if response.json().get("detail", None) is not None:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail"))
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json() if response.content else "Failed to get current user")

        return response.json()

    async def 验证角色_from_header(
            self,
            info: 请求_验证角色_from_header,
            token: str = Depends(oauth2_scheme)) -> 返回_验证角色_from_header:
        # 调用用户管理微服务进行角色验证
        async with httpx.AsyncClient() as client:
            # url demo: http://localhost:8101/api/roles/role-auth/
            response = await client.post(
                f"{self.svc_user}/api/roles/role-auth/",
                json=请求_验证角色_from_header(role_name=info.role_name, app_name=info.app_name).model_dump_json(),
                headers={"Authorization": f"Bearer {token}"}
            )

            if response.status_code != 200:
                if response.json().get("detail", None) is not None:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=response.json().get("detail"))
                else:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=response.json() if response.content else "Failed to auth role")

            return response.json()

    async def 发送验证码(self, phone: str) -> dict:
        # 调用用户管理微服务发送验证码
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.svc_user}/api/account/send-verification-code/",
                params={"phone": phone}
            )
            if response.status_code != 200:
                if response.json().get("detail", None) is not None:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=response.json().get("detail"))
                else:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=response.json() if response.content else "Failed to send verification code")
            return response.json()

    async def 注册_手机(self, data: 请求_手机邮箱_注册) -> 返回_login:
        # 调用用户管理微服务进行手机注册
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.svc_user}/api/account/register-phone/",
                json=data.model_dump()
            )
            if response.status_code != 200:
                if response.json().get("detail", None) is not None:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=response.json().get("detail"))
                else:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=response.json() if response.content else "Failed to register with phone")
            return response.json()

    async def 登录_手机(self, data: 请求_手机邮箱_登录) -> 返回_login:
        # 调用用户管理微服务进行手机登录
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.svc_user}/api/account/login-phone/",
                json=data.model_dump()
            )
            if response.status_code != 200:
                if response.json().get("detail", None) is not None:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=response.json().get("detail"))
                else:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=response.json() if response.content else "Failed to login with phone")
            return response.json()

    async def 更换绑定手机号(self, new_phone: str, sms_code: str, token: str = Depends(oauth2_scheme)) -> 返回_login:
        # 调用用户管理微服务更换绑定手机号
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.svc_user}/api/account/change-phone/",
                params={"new_phone": new_phone, "sms_code": sms_code},
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code != 200:
                if response.json().get("detail", None) is not None:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=response.json().get("detail"))
                else:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=response.json() if response.content else "Failed to change phone number")
            return response.json()
