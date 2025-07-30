"""
# File       : schemes.py
# Time       ：2024/8/26 下午8:53
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from typing import Union, Optional
from pydantic import BaseModel, Field, field_validator


class Payload_Role(BaseModel):
    role_name: str
    app_name: str
    app_id: int


class Payload(BaseModel):
    sub: str = Field(..., title="username", description="必须为用户表中的username字段，且类型必须为str, 否则会报错")
    username: Union[str, None] = None
    nickname: Union[str, None] = None
    roles: list[Payload_Role] = Field(..., title="角色", description="用户角色")


class 请求_获取_登录二维码URL(BaseModel):
    WECHAT_REDIRECT_URI: str


class 返回_login(BaseModel):
    access_token: str
    refresh_token: str
    user_info: Payload


class 请求_更新Token(BaseModel):
    refresh_token: str


class 返回_更新Token(BaseModel):
    access_token: str
    refresh_token: str


class 请求_检查Token_from_body(BaseModel):
    access_token: str


class 请求_验证角色_from_header(BaseModel):
    role_name: str
    app_name: str


class 返回_验证角色_from_header(BaseModel):
    status: bool


class 请求_分配或创建角色(BaseModel):
    user_id: int
    role_name: str
    app_name: str


class 返回_分配或创建角色(BaseModel):
    status: bool
    message: str


class 返回_获取_登录二维码URL(BaseModel):
    qr_code_url: str


class 请求_账号密码_注册(BaseModel):
    username: str
    password: str
    # 增加初始权限
    role_name: str = "l0"
    app_name: str = "app0"

    @field_validator('password')
    @classmethod
    def password_complexity(cls, v):
        if len(v) < 4:
            raise ValueError('Password must be at least 8 characters long')
        # if not any(char.isdigit() for char in v):
        #     raise ValueError('Password must contain at least one digit')
        # if not any(char.isalpha() for char in v):
        #     raise ValueError('Password must contain at least one letter')
        return v


class 请求_账号密码_登录(BaseModel):
    username: str
    password: str


class 请求_手机邮箱_注册(BaseModel):
    phone: str
    sms_code: str
    email: str = ""
    email_code: str = ""
    # 增加初始权限
    role_name: str = "l0"
    app_name: str = "app0"


class 请求_手机邮箱_登录(BaseModel):
    phone: str = ""
    sms_code: str = ""
    email: str = ""
    email_code: str = ""
