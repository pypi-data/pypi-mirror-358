import httpx
from typing import List, Optional
from app_tools_zxw.models_payment import PaymentMethod, OrderStatus
from app_tools_zxw.msvc_order_payments.schemas_通用管理 import (
    返回_获取所有产品, 返回_创建产品, 返回_更新产品, 返回_获取产品,
    返回_获取所有订单, 返回_创建订单, 返回_更新订单状态, 返回_获取订单,
    返回_获取所有支付, 返回_创建支付, 返回_获取支付
)
from app_tools_zxw.msvc_order_payments.__interface通用方法__ import 验证请求异常sync


class 通用管理:
    BASE_URL = "http://127.0.0.1:8102"  # 替换为实际的API基础URL

    def __init__(self, base_url: str):
        self.BASE_URL = base_url

    async def 获取所有产品(self) -> 返回_获取所有产品:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.BASE_URL}/products")
            验证请求异常sync(response)
            return 返回_获取所有产品(**response.json())

    async def 创建产品(self, name: str, app_id: str, price: float) -> 返回_创建产品:
        async with httpx.AsyncClient() as client:
            data = {"name": name, "app_id": app_id, "price": price}
            response = await client.post(f"{self.BASE_URL}/products", json=data)
            验证请求异常sync(response)
            return 返回_创建产品(**response.json())

    async def 更新产品(self, product_id: int, name: Optional[str] = None,
                       price: Optional[float] = None) -> 返回_更新产品:
        async with httpx.AsyncClient() as client:
            data = {"name": name, "price": price}
            response = await client.put(f"{self.BASE_URL}/products/{product_id}", json=data)
            验证请求异常sync(response)
            return 返回_更新产品(**response.json())

    async def 获取产品(self, product_id: int) -> 返回_获取产品:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.BASE_URL}/products/{product_id}")
            验证请求异常sync(response)
            return 返回_获取产品(**response.json())

    async def 获取所有订单(self) -> 返回_获取所有订单:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.BASE_URL}/orders")
            验证请求异常sync(response)
            return 返回_获取所有订单(**response.json())

    async def 创建订单(self, user_id: str, app_id: str, total_amount: float, product_id: int) -> 返回_创建订单:
        async with httpx.AsyncClient() as client:
            data = {"user_id": user_id, "app_id": app_id, "total_amount": total_amount, "product_id": product_id}
            response = await client.post(f"{self.BASE_URL}/orders", json=data)
            验证请求异常sync(response)
            return 返回_创建订单(**response.json())

    async def 更新订单状态(self, order_id: int, status: OrderStatus) -> 返回_更新订单状态:
        async with httpx.AsyncClient() as client:
            data = {"status": status}
            response = await client.put(f"{self.BASE_URL}/orders/{order_id}/status", json=data)
            验证请求异常sync(response)
            return 返回_更新订单状态(**response.json())

    async def 获取订单(self, order_id: int) -> 返回_获取订单:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.BASE_URL}/orders/{order_id}")
            验证请求异常sync(response)
            return 返回_获取订单(**response.json())

    async def 获取所有支付(self) -> 返回_获取所有支付:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.BASE_URL}/payments")
            验证请求异常sync(response)
            return 返回_获取所有支付(**response.json())

    async def 创建支付(self,
                       app_id: str,
                       order_id: int,
                       payment_method: PaymentMethod,
                       amount: float,
                       transaction_id: str,
                       payment_status: str,
                       callback_url: Optional[str] = None
                       ) -> 返回_创建支付:
        async with httpx.AsyncClient() as client:
            data = {
                "app_id": app_id,
                "order_id": order_id,
                "payment_method": payment_method,
                "amount": amount,
                "transaction_id": transaction_id,
                "payment_status": payment_status,
                "callback_url": callback_url
            }
            response = await client.post(f"{self.BASE_URL}/payments", json=data)
            验证请求异常sync(response)
            return 返回_创建支付(**response.json())

    async def 获取支付(self, payment_id: int) -> 返回_获取支付:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.BASE_URL}/payments/{payment_id}")
            验证请求异常sync(response)
            return 返回_获取支付(**response.json())
