"""
# File       : __interface通用方法__.py
# Time       ：2024/8/29 上午11:46
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from httpx import Response
from app_tools_zxw.Errors.api_errors import HTTPException_AppToolsSZXW


def 验证请求异常sync(response: Response):
    if response.status_code != 200:
        print("创建订单_alipay_pay_qr_create_order__post, status_code = ", response.status_code)
        print("创建订单_alipay_pay_qr_create_order__post, res = ", response.content)
        res = response.json()
        raise HTTPException_AppToolsSZXW(
            error_code=res["detail"].get("error_code", -9),
            http_status_code=response.status_code,
            detail=res["detail"].get("detail", "Unknown error"))
