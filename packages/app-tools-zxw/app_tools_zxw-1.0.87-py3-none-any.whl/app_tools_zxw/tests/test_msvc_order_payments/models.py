from sqlalchemy import Column, String, Integer, Float, ForeignKey, Enum, DateTime, func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app_tools_zxw.models_payment import OrderStatus, PaymentMethod

Base = declarative_base()
DATABASE_URL = "postgresql+asyncpg://my_zxw:my_zxw@127.0.0.1:5433/svc_order"
# 创建异步引擎
# engine = create_async_engine(DATABASE_URL, echo=False)
# AsyncSessionLocal = sessionmaker(bind=engine,
#                                  class_=AsyncSession,
#                                  expire_on_commit=False)
# 创建同步引擎，用于表结构的创建
# sync_engine = create_engine(DATABASE_URL)


# async def get_db():
#     async with AsyncSessionLocal() as session:
#         yield session
#
#
# def get_db_sync():
#     db = sync_engine.connect()
#     try:
#         yield db
#     finally:
#         db.close()


class Product(Base):
    """产品表"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    app_id = Column(String, index=True)  # The ID of the router the product belongs to
    price = Column(Float, nullable=False)

    # 懒加载的参数是指定在访问orders属性时，是否加载关联的Order对象
    orders = relationship("Order", back_populates="product")

    def to_dict(self) -> dict:
        data = {
            "id": self.id,
            "name": self.name,
            "app_id": self.app_id,
            "price": self.price,
            # "orders": [order.to_dict() for order in self.orders]
        }
        return data


class Order(Base):
    """订单表"""
    __tablename__ = "orders"
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, index=True)
    user_id = Column(String, index=True)
    app_id = Column(String, index=True)  # 新增字段，订单所属的app_id

    total_amount = Column(Float, nullable=False)  # 订单总金额
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)

    product_id = Column(Integer, ForeignKey("products.id"))
    product = relationship("Product", back_populates="orders")
    payments = relationship("Payment", back_populates="order")

    def to_dict(self) -> dict:
        data = {
            "id": self.id,
            "order_number": self.order_number,
            "user_id": self.user_id,
            "app_id": self.app_id,
            "total_amount": self.total_amount,
            "status": self.status.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "product_id": self.product_id,
            # "product": self.product.to_dict(),
            # "payments": [payment.to_dict() for payment in self.payments]
        }
        return data


class Payment(Base):
    """支付记录表"""
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())  # 自动更新时间

    app_id = Column(String, index=True)  # 新增字段，支付所属的app_id
    order_id = Column(Integer, ForeignKey("orders.id"))
    transaction_id = Column(String, unique=True)  # order_number 阿里支付的交易号

    amount = Column(Float, nullable=False)  # 支付金额
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    payment_status = Column(String)

    callback_url = Column(String, nullable=True)
    payment_url = Column(String, nullable=True)

    order = relationship("Order", back_populates="payments")

    def to_dict(self) -> dict:
        data = {
            "id": self.id,
            "app_id": self.app_id,
            "order_id": self.order_id,
            "payment_method": self.payment_method.value,
            "amount": self.amount,
            "transaction_id": self.transaction_id,
            "payment_status": self.payment_status,
            "callback_url": self.callback_url,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            # "order": self.order.to_dict()
        }
        return data
