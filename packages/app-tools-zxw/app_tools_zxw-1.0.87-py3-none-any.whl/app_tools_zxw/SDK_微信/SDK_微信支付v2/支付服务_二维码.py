"""
# File       : 微信支付.py
# Time       ：2024/8/25 07:11
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
import json
from uuid import uuid4
import hashlib
import httpx
from fastapi import HTTPException
from app_tools_zxw.models_payment import PaymentMethod
import xml.etree.ElementTree as ET


def dict_to_xml(tag, d):
    elem = ET.Element(tag)
    for key, val in d.items():
        child = ET.SubElement(elem, key)
        child.text = str(val)
    return elem


class 支付服务_二维码等:
    def __init__(self, app_id: str, mch_id: str, wechatpay_key: str):
        self.app_id = app_id  # 微信支付分配的公众账号ID
        self.mch_id = mch_id  # 微信支付分配的商户号
        self.key = wechatpay_key  # KEY

    async def 生成支付链接(self,
                           支付方式: PaymentMethod,
                           交易号: str,
                           金额: float,
                           回调地址: str,
                           用户ip地址: str,
                           商品描述: str = "二维码支付") -> str:
        if 支付方式 == PaymentMethod.WECHAT_QR:
            trade_type = "NATIVE"
        elif 支付方式 == PaymentMethod.WECHAT_H5:
            trade_type = "MWEB"
        elif 支付方式 == PaymentMethod.WECHAT_APP:
            trade_type = "APP"
        else:
            print(支付方式, PaymentMethod.WECHAT_QR, 支付方式 == PaymentMethod.WECHAT_QR)
            raise HTTPException(status_code=400, detail=f"不支持的支付方式,{支付方式.value}")

        # 生成支付链接
        url = "https://api.mch.weixin.qq.com/pay/unifiedorder"
        请求数据 = {
            "appid": self.app_id,
            "mch_id": self.mch_id,
            "nonce_str": 支付服务_二维码等.生成订单号(),
            "body": 商品描述,
            "out_trade_no": 交易号,
            "total_fee": int(金额 * 100),  # 单位为分
            "spbill_create_ip": 用户ip地址,
            "notify_url": 回调地址,
            "trade_type": trade_type,  # 使用NATIVE表示二维码支付
        }

        # 签名计算
        签名字符串 = "&".join([f"{k}={v}" for k, v in sorted(请求数据.items())]) + f"&key={self.key}"
        请求数据["sign"] = hashlib.md5(签名字符串.encode('utf-8')).hexdigest().upper()

        # 将请求数据转换为XML
        请求XML = ET.tostring(dict_to_xml("xml", 请求数据), encoding='utf-8')

        # 发起异步请求
        async with httpx.AsyncClient() as 客户端:
            响应 = await 客户端.post(url, data=请求XML, headers={'Content-Type': 'application/xml'})
            # 响应 = await 客户端.post(url, data=请求数据)

        # 解析返回值
        if 响应.status_code == 200:
            print(响应.text)  # 输出返回的原始内容
            try:
                响应数据 = 响应.json()
            except json.JSONDecodeError:
                print("### 支付ERROR ###")
                print("SDK_微信支付_二维码.py: 生成支付链接: 微信API返回了非JSON格式的数据 , 响应.text:", 响应.text)
                raise HTTPException(status_code=500, detail="微信API返回了非JSON格式的数据")

            if 响应数据.get("return_code") == "SUCCESS" and 响应数据.get("result_code") == "SUCCESS":
                return 响应数据["code_url"]  # 微信支付二维码链接
            else:
                raise HTTPException(status_code=400, detail="微信支付错误")
        else:
            raise HTTPException(status_code=500, detail="微信API错误")

    @staticmethod
    def 生成订单号() -> str:
        原始订单号 = str(uuid4())  # 或者其他生成逻辑
        return hashlib.md5(原始订单号.encode('utf-8')).hexdigest()
