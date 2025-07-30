"""
# File       : models.py
# Time       ：2024/8/25 11:06
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from typing import List
from pydantic import BaseModel


class callback支付结果pydantic(BaseModel):
    subject: str = "测试订单"
    gmt_payment: str = "2016-11-16 11:42:19"
    charset: str = "utf-8"
    seller_id: str = "xxxx"
    trade_status: str = "TRADE_SUCCESS"
    buyer_id: str = "xxxx"
    auth_app_id: str = "xxxx"
    buyer_pay_amount: str = "0.01"
    version: str = "1.0"
    gmt_create: str = "2016-11-16 11:42:18"
    trade_no: str = "xxxx"
    fund_bill_list: str = "[{\"amount\":\"0.01\",\"fundChannel\":\"ALIPAYACCOUNT\"}]"
    app_id: str = "xxxx"
    notify_time: str = "2016-11-16 11:42:19"
    point_amount: str = "0.00"
    total_amount: str = "0.01"
    notify_type: str = "trade_status_sync"
    out_trade_no: str = "xxxx"
    buyer_logon_id: str = "xxxx"
    notify_id: str = "xxxx"
    seller_email: str = "xxxx"
    receipt_amount: str = "0.01"
    invoice_amount: str = "0.01"
    sign: str = "xxx"


class 退款查询返回结果pydantic(BaseModel):
    code: str = '10000'
    msg: str = 'Success'
    out_request_no: str = '20171120'
    out_trade_no: str = '20171120'
    refund_amount: str = '20.00'
    total_amount: str = '20.00'
    trade_no: str = '2017112021001004070200297107'


class _订单查询_fund_bill_list(BaseModel):
    amount: str = "20.00"
    fund_channel: str = "ALIPAYACCOUNT"


class _订单查询_alipay_trade_query_response(BaseModel):
    trade_no: str = "2017032121001004070200176844"
    code: str = "10000"
    invoice_amount: str = "20.00"
    open_id: str = "20880072506750308812798160715407"
    fund_bill_list: List[_订单查询_fund_bill_list]
    buyer_logon_id: str = "csq***@sandbox.com"
    send_pay_date: str = "2017-03-21 13:29:17"
    receipt_amount: str = "20.00"
    out_trade_no: str = "out_trade_no15"
    buyer_pay_amount: str = "20.00"
    buyer_user_id: str = "2088102169481075"
    msg: str = "Success"
    point_amount: str = "0.00"
    trade_status: str = "TRADE_SUCCESS"
    total_amount: str = "20.00"


class 订单查询返回值pydantic(BaseModel):
    alipay_trade_query_response: _订单查询_alipay_trade_query_response
    sign: str


class 订单查询pydantic(BaseModel):
    code: str = '40004'
    msg: str = 'Business Failed'
    sub_code: str = 'ACQ.TRADE_NOT_EXIST'
    sub_msg: str = '交易不存在'
    buyer_pay_amount: str = '0.00'
    invoice_amount: str = '0.00'
    out_trade_no: str = '23131312'
    point_amount: str = '0.00'
    receipt_amount: str = '0.00'
    # success params
    buyer_logon_id: str = 'zxw***@gmail.com'
    buyer_user_id: str = '2088002912153711'
    send_pay_date: str = '2020-07-09 07:07:53'
    total_amount: str = '0.01'
    trade_no: str = '2020070922001453711429208912'
    trade_status: str = 'TRADE_SUCCESS'
