"""
# File       : 返回值模型.py
# Time       ：2024/8/24 09:29
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from pydantic import BaseModel, Field


class Return生成预支付单(BaseModel):
    return_code: str = Field(..., description="返回代码", examples=["SUCCESS"])
    return_msg: str = Field(..., description="返回信息", examples=["success"])
    appid: str = Field(..., description="公众账号ID", examples=["wx7d7eafcea994448d"])
    mch_id: str = Field(..., description="商户号", examples=["1517525131"])
    device_info: str = Field(..., description="设备号", examples=["aaa"])
    nonce_str: str = Field(..., description="随机字符串", examples=["vm6ERYl0bHM44Gue"])
    sign: str = Field(..., description="签名", examples=["5020D66BEA8618BE11B7445732EBD75C"])
    result_code: str = Field(..., description="业务结果", examples=["SUCCESS"])
    prepay_id: str = Field(..., description="预支付交易会话标识", examples=["wx061150043669000cbd492a3b1886276400"])
    trade_type: str = Field(..., description="交易类型", examples=["JSAPI"])
    timeStamp: str = Field(..., description="时间戳", examples=["1583466604"])
    paySign: str = Field(..., description="支付签名", examples=["a7d89c1f00c0a2d008e3e8a995fe7478"])
    signType: str = Field(..., description="签名类型", examples=["MD5"])
    out_trade_no: str = Field(..., description="商户订单号", examples=["自动生成"])


class Response查询订单(BaseModel):
    return_code: str = Field(..., description="返回代码", examples=["SUCCESS"])
    return_msg: str = Field(..., description="返回信息", examples=["success"])
    appid: str = Field(..., description="公众账号ID", examples=["wx7d7eafcea994448d"])
    mch_id: str = Field(..., description="商户号", examples=["1517525131"])
    device_info: str = Field(..., description="设备号", examples=["adsada"])
    nonce_str: str = Field(..., description="随机字符串", examples=["EmuBUAV6KcR7EtWk"])
    sign: str = Field(..., description="签名", examples=["1C37DBE29CDA93450D11A513F26DCEEE"])
    result_code: str = Field(..., description="业务结果", examples=["SUCCESS"])
    openid: str = Field(..., description="用户标识", examples=["oeb1N5S4BRkO4N0g1Ik53N4EDtDY"])
    is_subscribe: str = Field(..., description="是否关注公众账号", examples=["N"])
    trade_type: str = Field(..., description="交易类型", examples=["JSAPI"])
    bank_type: str = Field(..., description="付款银行", examples=["CMB_CREDIT"])
    total_fee: str = Field(..., description="订单金额", examples=["1"])
    fee_type: str = Field(..., description="货币种类", examples=["CNY"])
    transaction_id: str = Field(..., description="微信支付订单号", examples=["4200000264201903076947958032"])
    out_trade_no: str = Field(..., description="商户订单号", examples=["20190307162721_19814"])
    attach: str = Field(..., description="附加数据", examples=["None"])
    time_end: str = Field(..., description="支付完成时间", examples=["20190307162728"])
    trade_state: str = Field(..., description="交易状态", examples=["SUCCESS"])
    cash_fee: str = Field(..., description="现金支付金额", examples=["1"])
    trade_state_desc: str = Field(..., description="交易状态描述", examples=["支付成功"])
