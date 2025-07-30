import pytest
# from app_tools_zxw.msvc_order_payments.schemas_通用管理 import *
from app_tools_zxw.msvc_order_payments.interface_通用管理 import *
from app_tools_zxw.models_payment import PaymentMethod, OrderStatus

product_id = -9
if通用管理 = 通用管理(base_url="http://127.0.0.1:8102")


@pytest.mark.asyncio
async def test_获取所有产品():
    result = await if通用管理.获取所有产品()
    assert isinstance(result, 返回_获取所有产品)
    assert len(result.products) > 0


@pytest.mark.asyncio
async def test_创建产品():
    name = "Test Product"
    app_id = "test_app_id"
    price = 9.99
    result = await if通用管理.创建产品(name, app_id, price)

    assert isinstance(result, 返回_创建产品)
    global product_id
    product_id = result.id
    assert result.name == name
    assert result.app_id == app_id
    assert result.price == price


@pytest.mark.asyncio
async def test_更新产品():
    # 假设我们知道一个已存在的产品ID
    global product_id
    new_name = "Updated Test Product"
    new_price = 19.99
    result = await if通用管理.更新产品(product_id, name=new_name, price=new_price)
    assert isinstance(result, 返回_更新产品)
    assert result.name == new_name
    assert result.price == new_price


@pytest.mark.asyncio
async def test_获取产品():
    # 假设我们知道一个已存在的产品ID
    global product_id
    result = await if通用管理.获取产品(product_id)
    assert isinstance(result, 返回_获取产品)
    assert result.id == product_id


@pytest.mark.asyncio
async def test_获取所有订单():
    result = await if通用管理.获取所有订单()
    assert isinstance(result, 返回_获取所有订单)
    assert len(result.orders) > 0


@pytest.mark.asyncio
async def test_创建订单():
    user_id = "test_user"
    app_id = "test_app_id"
    total_amount = 29.99
    global product_id
    result = await if通用管理.创建订单(user_id, app_id, total_amount, product_id)
    assert isinstance(result, 返回_创建订单)
    assert result.user_id == user_id
    assert result.app_id == app_id
    assert result.total_amount == total_amount
    assert result.product_id == product_id


@pytest.mark.asyncio
async def test_更新订单状态():
    # 假设我们知道一个已存在的订单ID
    order_id = 1
    new_status = OrderStatus.PAID
    result = await if通用管理.更新订单状态(order_id, new_status)
    assert isinstance(result, 返回_更新订单状态)
    assert result.status == new_status


@pytest.mark.asyncio
async def test_获取订单():
    # 假设我们知道一个已存在的订单ID
    order_id = 1
    result = await if通用管理.获取订单(order_id)
    assert isinstance(result, 返回_获取订单)
    assert result.id == order_id


@pytest.mark.asyncio
async def test_获取所有支付():
    result = await if通用管理.获取所有支付()
    assert isinstance(result, 返回_获取所有支付)
    assert len(result.payments) > 0


@pytest.mark.asyncio
async def test_创建支付():
    app_id = "test_app_id"
    order_id = 1
    payment_method = PaymentMethod.WECHAT_H5
    amount = 29.99
    transaction_id = "test_transaction_id"
    payment_status = "pending"
    callback_url = "http://example.com/callback"
    result = await if通用管理.创建支付(app_id, order_id, payment_method, amount, transaction_id, payment_status,
                                       callback_url)
    assert isinstance(result, 返回_创建支付)
    assert result.app_id == app_id
    assert result.order_id == order_id
    assert result.payment_method == payment_method
    assert result.amount == amount
    assert result.transaction_id == transaction_id
    assert result.payment_status == payment_status
    assert result.callback_url == callback_url


@pytest.mark.asyncio
async def test_获取支付():
    # 假设我们知道一个已存在的支付ID
    payment_id = 1
    result = await if通用管理.获取支付(payment_id)
    assert isinstance(result, 返回_获取支付)
    assert result.id == payment_id
