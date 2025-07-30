"""
# File       : interface_支付宝支付.py
# Time       ：2024/8/29 上午10:47
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
import httpx
from app_tools_zxw.msvc_order_payments.schemas_微信支付宝支付 import (
    请求_支付宝url_创建订单,
    返回_支付宝url_订单信息,
    请求_支付宝url_发起支付,
    返回_支付宝url_支付信息
)
from app_tools_zxw.msvc_order_payments.__interface通用方法__ import 验证请求异常sync


class 支付宝支付:
    BASE_URL = "http://127.0.0.1:8002"  # Replace with the actual base URL

    def __init__(self, base_url=None):
        if base_url:
            self.BASE_URL = base_url

    async def 创建订单(self, amount: float,
                       user_id: str,
                       product_id: int,
                       app_id: str) -> 返回_支付宝url_订单信息:
        url = f"{self.BASE_URL}/alipay/pay_qr/create_order/"
        payload = 请求_支付宝url_创建订单(
            amount=amount,
            user_id=user_id,
            product_id=product_id,
            app_id=app_id
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload.dict())
            验证请求异常sync(response)
            res = response.json()
            print("创建订单_alipay_pay_qr_create_order__post", res)
            return 返回_支付宝url_订单信息(**res)

    async def 发起支付(self, order_number: str,
                       callback_url: str) -> 返回_支付宝url_支付信息:
        url = f"{self.BASE_URL}/alipay/pay_qr/pay/"
        payload = 请求_支付宝url_发起支付(
            order_number=order_number,
            callback_url=callback_url
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload.dict())
            验证请求异常sync(response)
            return 返回_支付宝url_支付信息(**response.json())

    async def 查询支付状态(self, transaction_id: str) -> 返回_支付宝url_支付信息:
        url = f"{self.BASE_URL}/alipay/pay_qr/payment_status/{transaction_id}"

        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            验证请求异常sync(response)
            return 返回_支付宝url_支付信息(**response.json())
