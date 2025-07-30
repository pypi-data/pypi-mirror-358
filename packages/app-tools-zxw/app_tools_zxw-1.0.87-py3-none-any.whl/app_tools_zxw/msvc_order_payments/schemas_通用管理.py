"""
# File       : schema_2.py
# Time       ：2024/8/28 下午12:43
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from app_tools_zxw.models_payment import PaymentMethod, OrderStatus


class ProductBase(BaseModel):
    name: str = Field(..., description="产品名称")
    app_id: str = Field(..., description="产品所属的应用ID")
    price: float = Field(..., description="产品价格")


class 请求_创建产品(ProductBase):
    pass


class 返回_创建产品(ProductBase):
    id: int = Field(..., description="产品ID")


class 请求_更新产品(BaseModel):
    name: Optional[str] = Field(None, description="产品名称")
    price: Optional[float] = Field(None, description="产品价格")


class 返回_更新产品(ProductBase):
    class Config:
        from_attributes = True

    id: int = Field(..., description="产品ID")


class 返回_获取产品(ProductBase):
    id: int = Field(..., description="产品ID")


class 返回_获取所有产品(BaseModel):
    products: List[返回_获取产品] = Field(..., description="产品列表")


class OrderBase(BaseModel):
    user_id: str = Field(..., description="用户ID")
    app_id: str = Field(..., description="订单所属的应用ID")
    total_amount: float = Field(..., description="订单总金额")
    product_id: int = Field(..., description="产品ID")


class 请求_创建订单(OrderBase):
    pass


class 返回_创建订单(OrderBase):
    id: int = Field(..., description="订单ID")
    order_number: str = Field(..., description="订单编号")
    status: OrderStatus = Field(..., description="订单状态")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class 请求_更新订单状态(BaseModel):
    status: OrderStatus = Field(..., description="新的订单状态")


class 返回_更新订单状态(BaseModel):
    id: int = Field(..., description="订单ID")
    order_number: str = Field(..., description="订单编号")
    status: OrderStatus = Field(..., description="更新后的订单状态")
    updated_at: datetime = Field(..., description="更新时间")


class 返回_获取订单(OrderBase):
    id: int = Field(..., description="订单ID")
    order_number: str = Field(..., description="订单编号")
    status: OrderStatus = Field(..., description="订单状态")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class 返回_获取所有订单(BaseModel):
    orders: List[返回_获取订单] = Field(..., description="订单列表")


class PaymentBase(BaseModel):
    app_id: str = Field(..., description="支付所属的应用ID")
    order_id: int = Field(..., description="关联的订单ID")
    payment_method: PaymentMethod = Field(..., description="支付方式")
    amount: float = Field(..., description="支付金额")
    transaction_id: str = Field(..., description="交易ID")
    payment_status: str = Field(..., description="支付状态")
    callback_url: Optional[str] = Field(None, description="回调URL")


class 请求_创建支付(PaymentBase):
    pass


class 返回_创建支付(PaymentBase):
    id: int = Field(..., description="支付记录ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class 返回_获取支付(PaymentBase):
    id: int = Field(..., description="支付记录ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class 返回_获取所有支付(BaseModel):
    payments: List[返回_获取支付] = Field(..., description="支付记录列表")
