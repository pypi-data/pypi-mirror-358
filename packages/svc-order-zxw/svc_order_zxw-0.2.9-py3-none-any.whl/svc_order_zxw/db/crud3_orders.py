"""
# File       : crud3_orders.py
# Time       ：2024/10/7 06:26
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from pydantic import BaseModel, Field
from datetime import datetime
from svc_order_zxw.apis.schemas_payments import OrderStatus, PaymentMethod
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from svc_order_zxw.db.models import Order, Product
from typing import List, Optional, Union
from sqlalchemy.orm import joinedload

from app_tools_zxw.Funcs.生成订单号 import 生成订单号
from app_tools_zxw.Errors.api_errors import HTTPException_AppToolsSZXW
from svc_order_zxw.异常代码 import 订单_异常代码, 其他_异常代码


class PYD_OrderBase(BaseModel):
    user_id: str
    total_price: float
    quantity: int = Field(default=1)


class PYD_OrderCreate(PYD_OrderBase):
    order_number: str = 生成订单号()
    product_id: int


class PYD_OrderUpdate(BaseModel):
    total_price: Optional[float] = None
    quantity: Optional[int] = None


class PYD_ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    app_id: int


class PYD_ApplicationResponse(BaseModel):
    id: int
    name: str


class PYD_PaymentResponse(BaseModel):
    id: int
    payment_price: float
    payment_method: PaymentMethod
    payment_status: OrderStatus
    callback_url: Optional[str]
    payment_url: Optional[str]
    created_at: datetime
    updated_at: datetime


class PYD_OrderResponse(PYD_OrderBase):
    id: int
    order_number: str
    created_at: datetime
    updated_at: datetime
    product_id: int
    product: Optional[PYD_ProductResponse] = None
    application: Optional[PYD_ApplicationResponse] = None
    payment: Optional[PYD_PaymentResponse] = None

    class Config:
        from_attributes = True


class PYD_OrderFilter(BaseModel):
    user_id: Optional[str] = None
    product_id: Optional[int] = None
    application_id: Optional[int] = None


async def create_order(
        db: AsyncSession,
        order: PYD_OrderCreate,
        include_product: bool = False,
        include_application: bool = False,
        include_payment: bool = False) -> PYD_OrderResponse:
    try:
        new_order = Order(**order.model_dump())
        db.add(new_order)
        await db.commit()
        await db.refresh(new_order)

        if include_product:
            await db.refresh(new_order, attribute_names=['product'])
        if include_application:
            # 修改这里：分两步刷新 product 和 app
            await db.refresh(new_order, attribute_names=['product'])
            if new_order.product:
                await db.refresh(new_order.product, attribute_names=['app'])
        if include_payment:
            await db.refresh(new_order, attribute_names=['payment'])

        order_dict = {
            "id": new_order.id,
            "user_id": new_order.user_id,
            "total_price": new_order.total_price,
            "quantity": new_order.quantity,
            "order_number": new_order.order_number,
            "created_at": new_order.created_at,
            "updated_at": new_order.updated_at,
            "product_id": new_order.product_id,
        }

        if include_product and new_order.product:
            order_dict["product"] = PYD_ProductResponse(
                id=new_order.product.id,
                name=new_order.product.name,
                price=new_order.product.price,
                app_id=new_order.product.app_id
            )

        if include_application and new_order.product and new_order.product.app:
            order_dict["application"] = PYD_ApplicationResponse(
                id=new_order.product.app.id,
                name=new_order.product.app.name
            )

        if include_payment and new_order.payment:
            order_dict["payment"] = PYD_PaymentResponse(
                id=new_order.payment.id,
                payment_price=new_order.payment.payment_price,
                payment_method=new_order.payment.payment_method,
                payment_status=new_order.payment.payment_status,
                callback_url=new_order.payment.callback_url,
                payment_url=new_order.payment.payment_url,
                created_at=new_order.payment.created_at,
                updated_at=new_order.payment.updated_at
            )

        return PYD_OrderResponse(**order_dict)
    except Exception as e:
        await db.rollback()
        raise HTTPException_AppToolsSZXW(其他_异常代码.新增数据失败, f"创建订单失败: {str(e)}")


async def get_order(
        db: AsyncSession,
        order_identifier: Union[int, str],
        include_product: bool = False,
        include_application: bool = False,
        include_payment: bool = False) -> Optional[PYD_OrderResponse]:
    """
    获取指定订单的详细信息。

    参数:
    - db: AsyncSession - 数据库会话对象
    - order_identifier: Union[int, str] - 订单标识符，可以是订单ID（整数）或订单号（字符串）
    - include_product: bool - 是否包含关联的产品信，默认为False
    - include_application: bool - 是否包含关联的应用信息，默认为False
    - include_payment: bool - 是否包含关联的支付信息，默认为False

    返回:
    - Optional[PYD_OrderResponse] - 如果找到订单，返回订单响应对象；否则返回None

    说明:
    - 此函数支持通过订单ID或订单号查询订单
    - 如果include_product为True，将同时加载并返回关联的产品信息
    - 如果include_application为True，将同时加载并返回关联的应用信息
    - 如果include_payment为True，将同时加载并返回关联的支付信息
    """

    query = select(Order)

    if include_product:
        query = query.options(joinedload(Order.product))
    if include_application:
        query = query.options(joinedload(Order.product).joinedload(Product.app))
    if include_payment:
        query = query.options(joinedload(Order.payment))

    if isinstance(order_identifier, int):
        query = query.where(Order.id == order_identifier)
    else:
        query = query.where(Order.order_number == order_identifier)

    result = await db.execute(query)
    order = result.unique().scalar_one_or_none()

    if not order:
        return None
        # raise HTTPException_AppToolsSZXW(订单_异常代码.订单号不存在, f"未找到订单: {order_identifier}")

    # 手动加载关联关系
    # if include_product:
    #     await db.refresh(order, attribute_names=['product'])
    # if include_application:
    #     await db.refresh(order.product, attribute_names=['app'])
    # if include_payment:
    #     await db.refresh(order, attribute_names=['payment'])

    # 创建不包含关联关系的订单字典
    order_dict = {
        "id": order.id,
        "user_id": order.user_id,
        "total_price": order.total_price,
        "quantity": order.quantity,
        "order_number": order.order_number,
        "created_at": order.created_at,
        "updated_at": order.updated_at,
        "product_id": order.product_id,
    }

    # 如果包含产品信息，添加到字典中
    if include_product and order.product:
        order_dict["product"] = PYD_ProductResponse(
            id=order.product.id,
            name=order.product.name,
            price=order.product.price,
            app_id=order.product.app_id
        )

    # 如果包含应用信息，添加到字典中
    if include_application and order.product and order.product.app:
        order_dict["application"] = PYD_ApplicationResponse(
            id=order.product.app.id,
            name=order.product.app.name
        )

    # 如果包含支付信息，添加到字典中
    if include_payment and order.payment:
        order_dict["payment"] = PYD_PaymentResponse(
            id=order.payment.id,
            payment_price=order.payment.payment_price,
            payment_method=order.payment.payment_method,
            payment_status=order.payment.payment_status,
            callback_url=order.payment.callback_url,
            payment_url=order.payment.payment_url,
            created_at=order.payment.created_at,
            updated_at=order.payment.updated_at
        )

    return PYD_OrderResponse(**order_dict)


async def update_order(
        db: AsyncSession,
        order_id: int,
        order_update: PYD_OrderUpdate) -> Optional[PYD_OrderResponse]:
    try:
        # 首先获取现有订单
        query = select(Order).where(Order.id == order_id)
        result = await db.execute(query)
        order = result.scalar_one_or_none()

        if not order:
            raise HTTPException_AppToolsSZXW(订单_异常代码.订单号不存在, f"未找到要更新的订单: {order_id}")

        # 更新订单
        for field, value in order_update.dict(exclude_unset=True).items():
            setattr(order, field, value)

        await db.commit()
        await db.refresh(order)

        # 手动创建 PYD_OrderResponse 对象
        order_response = PYD_OrderResponse(
            id=order.id,
            user_id=order.user_id,
            total_price=order.total_price,
            quantity=order.quantity,
            order_number=order.order_number,
            created_at=order.created_at,
            updated_at=order.updated_at,
            product_id=order.product_id
        )

        return order_response
    except Exception as e:
        await db.rollback()
        raise HTTPException_AppToolsSZXW(其他_异常代码.更新数据失败, f"更新订单失败: {str(e)}")


async def delete_order(db: AsyncSession, order_id: int) -> bool:
    try:
        query = delete(Order).where(Order.id == order_id)
        result = await db.execute(query)
        await db.commit()
        if result.rowcount == 0:
            raise HTTPException_AppToolsSZXW(订单_异常代码.订单号不存在, f"未找到要删除的订单: {order_id}")
        return True
    except Exception as e:
        await db.rollback()
        raise HTTPException_AppToolsSZXW(其他_异常代码.删除数据失败, f"删除订单失败: {str(e)}")


async def list_orders(
        db: AsyncSession,
        filter: PYD_OrderFilter,
        skip: int = 0,
        limit: int = 100,
        include_product: bool = False,
        include_application: bool = False,
        include_payment: bool = False) -> List[PYD_OrderResponse]:
    query = select(Order)

    if include_product:
        query = query.options(joinedload(Order.product))
    if include_application:
        query = query.options(joinedload(Order.product).joinedload(Product.app))
    if include_payment:
        query = query.options(joinedload(Order.payment))

    if filter.user_id:
        query = query.where(Order.user_id == filter.user_id)
    if filter.product_id:
        query = query.where(Order.product_id == filter.product_id)
    if filter.application_id:
        query = query.join(Product).where(Product.app_id == filter.application_id)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    orders = result.unique().scalars().all()

    order_responses = []
    for order in orders:
        order_dict = {
            "id": order.id,
            "user_id": order.user_id,
            "total_price": order.total_price,
            "quantity": order.quantity,
            "order_number": order.order_number,
            "created_at": order.created_at,
            "updated_at": order.updated_at,
            "product_id": order.product_id,
        }

        if include_product and order.product:
            order_dict["product"] = PYD_ProductResponse(
                id=order.product.id,
                name=order.product.name,
                price=order.product.price,
                app_id=order.product.app_id
            )

        if include_application and order.product and order.product.app:
            order_dict["application"] = PYD_ApplicationResponse(
                id=order.product.app.id,
                name=order.product.app.name
            )

        if include_payment and order.payment:
            order_dict["payment"] = PYD_PaymentResponse(
                id=order.payment.id,
                payment_price=order.payment.payment_price,
                payment_method=order.payment.payment_method,
                payment_status=order.payment.payment_status,
                callback_url=order.payment.callback_url,
                payment_url=order.payment.payment_url,
                created_at=order.payment.created_at,
                updated_at=order.payment.updated_at
            )

        order_responses.append(PYD_OrderResponse(**order_dict))

    return order_responses
