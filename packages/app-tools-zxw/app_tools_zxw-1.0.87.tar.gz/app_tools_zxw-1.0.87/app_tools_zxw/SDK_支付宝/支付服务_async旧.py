"""
# File       : 支付服务_异步.py
# Time       ：2024/9/3 上午4:27
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from pathlib import Path
from typing import Union
from uuid import uuid4
import hashlib
from app_tools_zxw.models_payment import PaymentMethod, OrderStatus
from qrcode.main import QRCode
import qrcode
from pydantic import BaseModel, Field
from app_tools_zxw.SDK_支付宝.tools import crt证书_解析成_pem公钥
from alipay_zxw import AliPay
from app_tools_zxw.Errors.api_errors import HTTPException_AppToolsSZXW, ErrorCode
from fastapi import APIRouter, FastAPI


class PaymentResult(BaseModel):
    商户订单号: str = Field(..., title="商户订单号", description="transaction_id")
    支付平台交易号: str = Field(..., title="支付平台交易号", description="")
    交易金额: float = Field(..., title="交易金额", description="amount")
    交易状态: OrderStatus
    支付时间: str = Field(..., title="支付时间", description="payment_time")
    支付账号: str = None
    支付方式: PaymentMethod
    支付失败原因: str = None
    备注: str = None


class 支付服务:
    alipay_client: AliPay
    _回调路径的根地址 = "http://0.0.0.0"  # 如果需要回调处理的话，此处必填
    _回调路径 = "/callback/"

    def __init__(self, app_id: str,
                 key应用私钥: Union[str, Path],
                 key支付宝公钥: Union[str, Path],
                 回调路径的根地址: str):
        """
        :param app_id:
        :param key应用私钥: 路径 或 密匙
        :param key支付宝公钥: 路径 或 密匙
        :param 回调路径的根地址: 如果需要回调处理的话，此处必填
        """
        self._支付服务器根地址 = 回调路径的根地址

        # 读取密匙
        if isinstance(key支付宝公钥, Path):
            if key支付宝公钥.suffix == ".crt":
                key支付宝公钥 = crt证书_解析成_pem公钥(key支付宝公钥)
                print("app-tools-zxw/SDK_支付宝/支付服务_新SDK.py: key支付宝公钥=", key支付宝公钥)
            else:
                key支付宝公钥 = open(key支付宝公钥).read()
        if isinstance(key应用私钥, Path):
            if key应用私钥.suffix == ".crt":
                key应用私钥 = crt证书_解析成_pem公钥(key应用私钥)
                print("app-tools-zxw/SDK_支付宝/支付服务_新SDK.py: key应用私钥=", key应用私钥)
            else:
                key应用私钥 = open(key应用私钥).read()

        # 初始化支付宝客户端
        self.alipay_client = AliPay(
            appid=app_id,
            app_private_key_string=key应用私钥,
            alipay_public_key_string=key支付宝公钥,
            app_notify_url=self._回调路径的根地址 + self._回调路径,
            sign_type="RSA2",
            debug=False
        )

    @staticmethod
    def 生成订单号() -> str:
        原始订单号 = str(uuid4())  # 或者其他生成逻辑
        return hashlib.md5(原始订单号.encode('utf-8')).hexdigest()

    async def 发起二维码支付(self, 商户订单号: str, 价格: float, 商品名称: str) -> str:
        self.__订单信息校验(商户订单号, 价格, 商品名称)

        try:
            response = await self.alipay_client.api_alipay_trade_precreate(
                out_trade_no=商户订单号,
                total_amount=str(价格),
                subject=商品名称
            )
            print("发起二维码支付: response=", response)
        except Exception as e:
            raise HTTPException_AppToolsSZXW(
                error_code=400,
                http_status_code=400,
                detail=f"支付宝支付接口调用失败: {str(e)}"
            )

        if response.get("code") == "10000":
            qr_code_url = response.get("qr_code")
            return qr_code_url
        else:
            raise HTTPException_AppToolsSZXW(
                error_code=ErrorCode.支付宝支付接口调用失败,
                http_status_code=400,
                detail=f"支付宝支付接口调用失败: {response.get('msg')},{response.get('sub_msg')}"
            )

    async def 发起APP支付(self,
                          商户订单号: str,
                          价格: float,
                          商品名称="") -> str:
        self.__订单信息校验(商户订单号, 价格, 商品名称)
        # App支付，将order_string返回给app即可
        try:
            order_string = self.alipay_client.api_alipay_trade_app_pay(
                subject=商品名称,
                out_trade_no=商户订单号,
                total_amount=str(价格),
            )
            print("发起APP支付: order_string=", order_string)
            return order_string
        except Exception as e:
            raise HTTPException_AppToolsSZXW(
                error_code=400,
                http_status_code=400,
                detail=f"支付宝APP支付接口调用失败: {str(e)}"
            )

    async def 查询订单(self, 商户订单号: str) -> OrderStatus:
        try:
            response = await self.alipay_client.api_alipay_trade_query(out_trade_no=商户订单号)
            print("查询订单: response=", response)

            if response.get("code") == "10000":
                trade_status = response.get("trade_status")
                if trade_status == "TRADE_SUCCESS":
                    return OrderStatus.PAID
                elif trade_status == "WAIT_BUYER_PAY":
                    return OrderStatus.PENDING
                elif trade_status in ["TRADE_CLOSED", "TRADE_FINISHED"]:
                    return OrderStatus.FINISHED
                else:
                    return OrderStatus.FAILED
            else:
                raise HTTPException_AppToolsSZXW(
                    error_code=ErrorCode.支付宝支付接口调用失败,
                    http_status_code=400,
                    detail=f"查询订单失败: {response.get('msg')},{response.get('sub_msg')}"
                )
        except Exception as e:
            raise HTTPException_AppToolsSZXW(
                error_code=400,
                http_status_code=400,
                detail=f"查询订单接口调用失败: {str(e)}")

    async def 退款查询(self, 商户订单号: str) -> bool:
        try:
            response = await self.alipay_client.api_alipay_trade_fastpay_refund_query(
                out_trade_no=商户订单号,
                out_request_no=商户订单号
            )
            print("退款查询: response=", response)
            return response.get("code") == "10000"
        except Exception as e:
            raise HTTPException_AppToolsSZXW(
                error_code=ErrorCode.支付宝支付接口调用失败,
                http_status_code=400,
                detail=f"退款查询接口调用失败: {str(e)}"
            )

    def 注册回调接口(self, app, async_func_支付成功, dependencies: list = None):
        """
        注册回调接口
        :param app: FastAPI或APIRouter实例
        :param async_func_支付成功: 异步函数，处理支付成功后的逻辑
        :param dependencies: 可选的依赖注入列表，例如 [Depends(get_db), Depends(get_current_user)]
        """
        支付状态回调地址 = self._回调路径
        alipay_client = self.alipay_client

        @app.get(支付状态回调地址)
        async def 回调_验证地址(request):
            print("支付回调get请求：", request)
            return "ok"

        @app.post(支付状态回调地址)
        async def 回调_支付完成处理(postBody):
            """
            支付回调处理
            :param postBody: 请求体,类型：Request
            """
            # 整理数据
            formData = await postBody.form()  # 获取表单数据
            dataDict = {item[0]: item[1] for item in formData.items()}  # 将表单数据转换为字典
            print("支付回调post请求,dataDict=", dataDict)

            # 提取签名信息
            signature = dataDict.pop("sign", None)
            # 校验数据
            try:
                # 使用支付宝公钥和签名类型进行验证
                success = alipay_client.verify(dataDict, signature)
            except Exception as e:
                raise HTTPException_AppToolsSZXW(
                    error_code=ErrorCode.签名验证失败,
                    http_status_code=400,
                    detail=f"签名验证失败: {str(e)}"
                )

            # 校验成功，处理支付结果
            if not success:
                raise HTTPException_AppToolsSZXW(
                    error_code=ErrorCode.签名验证失败,
                    http_status_code=400,
                    detail="签名验证失败"
                )

            result = PaymentResult(
                商户订单号=dataDict.get("out_trade_no"),
                支付平台交易号=dataDict.get("trade_no"),
                交易金额=float(dataDict.get("total_amount")),
                交易状态=OrderStatus.PENDING,
                支付时间=dataDict.get("gmt_payment"),
                支付方式=PaymentMethod.ALIPAY_H5,
                支付账号=dataDict.get("buyer_logon_id"),
                备注=dataDict.get("body")
            )
            if dataDict.get("trade_status") == "TRADE_SUCCESS":
                result.交易状态 = OrderStatus.PAID
            elif dataDict.get("trade_status") == "TRADE_CLOSED":
                result.交易状态 = OrderStatus.FAILED
                result.支付失败原因 = dataDict.get("TRADE_CLOSED")
            elif dataDict.get("trade_status") == "TRADE_FINISHED":
                # 交易完成，不可退款.TRADE_FINISHED与TRADE_SUCCESS的区别是TRADE_FINISHED是不可退款的.
                result.交易状态 = OrderStatus.FINISHED
            else:
                result.支付失败原因 = dataDict.get("trade_status")
                result.交易状态 = OrderStatus.FAILED

            return await async_func_支付成功(result)

    @staticmethod
    def 生成二维码(qr_code_url: str):
        qr = QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_code_url)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        img.save("alipay_qr.png")
        print("二维码已生成，保存为 alipay_qr.png")

    @staticmethod
    def __订单信息校验(商户订单号: str, 价格: float, 商品名称: str):
        if not 商户订单号 or len(商户订单号) > 32:
            raise HTTPException_AppToolsSZXW(
                error_code=ErrorCode.商户订单号不能为空或超过32位,
                http_status_code=400,
                detail="商户订单号不能为空,或超过32位"
            )
        if not 价格 or 价格 <= 0:
            raise HTTPException_AppToolsSZXW(
                error_code=ErrorCode.价格不能为空或小于0,
                http_status_code=400,
                detail="价格不能为空,或小于0"
            )
        if not 商品名称:
            raise HTTPException_AppToolsSZXW(
                error_code=ErrorCode.商品名称不能为空,
                http_status_code=400,
                detail="商品名称不能为空"
            )
