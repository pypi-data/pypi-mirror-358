"""
# File       : 支付服务_规范.py
# Time       ：2024/8/26 06:26
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：适用于微信支付、支付宝支付、银联支付等支付服务的规范
支付宝支付适配完成
微信支付未适配
"""
from pathlib import Path
from typing import Union
import json
from uuid import uuid4
import hashlib
from fastapi import FastAPI, HTTPException, status, Request, APIRouter
from app_tools_zxw.models_payment import OrderStatus, PaymentResult


class 支付服务:
    _回调路径 = "/callback/alipay"

    def __init__(self):
        # 初始化 支付客户端
        ...

    @staticmethod
    def 生成订单号() -> str:
        原始订单号 = str(uuid4())  # 或者其他生成逻辑
        return hashlib.md5(原始订单号.encode('utf-8')).hexdigest()

    async def 发起二维码支付(self, 商户订单号: str, 价格: float, 商品名称: str) -> str:
        ...

    async def 查询订单(self, 商户订单号: str) -> OrderStatus:
        ...

    async def 退款查询(self, 商户订单号: str) -> bool:
        ...

    async def 注册回调接口(self, router: Union[FastAPI, APIRouter], async_func_支付成功):
        _回调路径 = self._回调路径

        @router.get(_回调路径)
        async def 回调_支付完成处理(request):
            print("支付回调get请求：", request)
            return "ok"

        @router.post(_回调路径)
        async def 回调_支付完成处理(postBody: Request) -> any:
            ...
            if "支付验证成功":
                data = PaymentResult(
                    # 从postBody中获取数据
                )
                return await async_func_支付成功(data)
            else:
                raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="支付失败")

    @staticmethod
    def __订单信息校验(商户订单号: str, 价格: float, 商品名称: str):
        if not 商户订单号 or len(商户订单号) > 32:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="商户订单号不能为空,或超过32位")
        if not 价格 or 价格 <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="价格不能为空,或小于0")
        if not 商品名称:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="商品名称不能为空")
