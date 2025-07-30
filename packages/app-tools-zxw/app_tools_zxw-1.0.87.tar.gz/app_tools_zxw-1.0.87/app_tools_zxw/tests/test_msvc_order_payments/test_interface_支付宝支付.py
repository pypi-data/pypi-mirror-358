import pytest
import asyncio
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app_tools_zxw.models_payment import OrderStatus, PaymentMethod
from app_tools_zxw.tests.test_msvc_order_payments.models import Product, DATABASE_URL
from app_tools_zxw.msvc_order_payments.schemas_微信支付宝支付 import (
    请求_支付宝url_创建订单,
    返回_支付宝url_订单信息,
    请求_支付宝url_发起支付,
    返回_支付宝url_支付信息,
)
from app_tools_zxw.msvc_order_payments.interface_支付宝支付 import 支付宝支付

# 数据库连接配置
DATABASE_URL = "postgresql+asyncpg://my_zxw:my_zxw@127.0.0.1:5433/svc_order"

# 创建支付宝支付接口
interface = 支付宝支付(base_url="http://127.0.0.1:8102")

# 创建异步引擎
engine = create_async_engine(DATABASE_URL, echo=True)

# 创建异步会话
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="module")
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Product.__table__.create, checkfirst=True)

    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Product.__table__.drop)


@pytest.fixture(scope="module")
async def test_product(db_session: AsyncSession):
    product = Product(
        name="Test Product",
        app_id="test_app",
        price=100.0
    )
    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)
    return product


@pytest.mark.asyncio
async def test_创建订单_alipay_pay_qr_create_order__post(test_product: Product):
    request = 请求_支付宝url_创建订单(
        amount=test_product.price,
        user_id="test_user",
        product_id=test_product.id,
        app_id=test_product.app_id
    )

    result = await interface.创建订单(**request.model_dump())

    assert isinstance(result, 返回_支付宝url_订单信息)
    assert result.total_amount == test_product.price
    assert result.status == OrderStatus.PENDING


@pytest.mark.asyncio
async def test_发起支付_alipay_pay_qr_pay__post(test_product: Product):
    # 首先创建一个订单
    create_order_request = 请求_支付宝url_创建订单(
        amount=test_product.price,
        user_id="test_user",
        product_id=test_product.id,
        app_id=test_product.app_id
    )
    order_result = await interface.创建订单(**create_order_request.model_dump())

    # 然后用这个订单发起支付
    request = 请求_支付宝url_发起支付(
        order_number=order_result.order_number,
        callback_url="http://test-callback.com"
    )

    result = await interface.发起支付(**request.model_dump())

    assert isinstance(result, 返回_支付宝url_支付信息)
    assert result.amount == test_product.price
    assert result.payment_status in ["pending", "processing", "success"]


@pytest.mark.asyncio
async def test_查询支付状态_alipay_pay_qr_payment_status__transaction_id__get(test_product: Product):
    # 首先创建一个订单并发起支付
    create_order_request = 请求_支付宝url_创建订单(
        amount=test_product.price,
        user_id="test_user",
        product_id=test_product.id,
        app_id=test_product.app_id
    )
    order_result = await interface.创建订单(**create_order_request.model_dump())

    pay_request = 请求_支付宝url_发起支付(
        order_number=order_result.order_number,
        callback_url="http://test-callback.com"
    )
    pay_result = await interface.发起支付(**pay_request.model_dump())

    # 然后查询支付状态
    result = await interface.查询支付状态(pay_result.transaction_id)

    assert isinstance(result, 返回_支付宝url_支付信息)
    assert result.transaction_id == pay_result.transaction_id
    assert result.payment_status in ["pending", "processing", "success", "failed"]


if __name__ == "__main__":
    pytest.main(["-v", __file__])
