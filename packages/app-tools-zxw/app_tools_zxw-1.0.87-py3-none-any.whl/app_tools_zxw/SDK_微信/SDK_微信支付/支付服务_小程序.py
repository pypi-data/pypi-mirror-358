"""
-----------微信支付api-----------
"""
import httpx
from uuid import uuid4
from app_tools_zxw.SDK_微信.SDK_微信支付 import minipay
from typing import Union
import hashlib
import time
from app_tools_zxw.SDK_微信.SDK_微信支付v2.返回值模型 import Return生成预支付单, Response查询订单


class 支付服务_小程序:
    @staticmethod
    def 生成订单号():
        return str(uuid4())

    @staticmethod
    async def 发起支付_小程序(openid,
                              支付金额=0,
                              商品编号='ZiDingYi',
                              商品描述='景募',
                              设备ID='aaa',
                              商户订单号='自动生成') -> tuple[bool, Union[Return生成预支付单, str]]:
        """
        直接传给前端使用
        :param openid:
        :param 支付金额:
        :param 商品编号:
        :param 商品描述:
        :param 设备ID:
        :param 商户订单号:
        :return: （下单是否成功，返回给前端的数据）
        """
        # 生成 商户订单号
        if 商户订单号 == '自动生成':
            商户订单号 = str(uuid4())  # 生成唯一订单号

        # 预下单
        uni = minipay.UnifiedOrder(out_trade_no=商户订单号,
                                   body=商品描述,
                                   openid=openid,
                                   device_info=设备ID,
                                   total_fee=支付金额,
                                   product_id=商品编号)
        response = await uni.request_async()

        # 下单失败
        if uni.is_success is False:
            return False, uni.error

        # 生成支付签名
        md5 = hashlib.md5()
        timeStamp = str(int(time.time()))
        key = 'zhanrowicjkd938123nxuenwkalwqpxi'
        strs = 'appId=%s&nonceStr=%s&package=prepay_id=%s&signType=MD5&timeStamp=%s&key=%s' \
               % (response['appid'], response['nonce_str'], response['prepay_id'], timeStamp, key)
        strs = strs.encode('utf-8')
        md5.update(strs)

        paySign = md5.hexdigest()

        # 返回给前端的数据
        response['timeStamp'] = timeStamp
        response['paySign'] = paySign
        response['signType'] = "MD5"
        response["out_trade_no"] = 商户订单号

        return True, Return生成预支付单(**response)

    @staticmethod
    async def 查询订单(商户订单号: str = 'abv2010102333112') -> tuple[bool, Union[Response查询订单, str]]:
        query = minipay.OrderQuery(out_trade_no=商户订单号)
        response = await query.request_async()
        if query.is_success:
            return True, Response查询订单(**response)
        else:
            print(query.error)
            print(response)
            return False, query.error

    @staticmethod
    async def 申请退款(refund_fee: int, total_fee: int, 商户订单号: str):
        # refund_fee = 100
        # total_fee = 200
        refund = minipay.Refund(
            out_trade_no=str(商户订单号),
            total_fee=total_fee,
            refund_fee=refund_fee,
            out_refund_no=str(商户订单号)
        )
        print("商户订单号,total_fee,refund_fee: ", 商户订单号, total_fee, refund_fee)
        # response = await refund.arequest()
        response = refund.request()
        if refund.is_success:
            print("退款成功")
            print(response)
            if response["result_code"] == "SUCCESS":
                return {"status": "SUCCESS", "tip": "退款申请提交成功。"}
            else:
                return {"status": "FAIL", "tip": response["err_code_des"]}
        else:
            print(response)
            print(商户订单号)
            return {"status": "FAIL", "tip": "执行退款->" + response["desc"]}

    @staticmethod
    async def 查询退款(商户订单号):
        # out_trade_no，out_refund_no，transaction_id三选1
        query = minipay.RefundQuery(out_trade_no=商户订单号)
        response = await query.request_async()
        if query.is_success:
            """
            成功 返回：
            {'appid': 'wx7d7eafcea994448d', 'cash_fee': '1', 'mch_id': '1517525131', 
            'nonce_str': '9CAwolVv3iFknDwy', 
            'out_refund_no_0': '2020013006215459919015339', 
            'out_trade_no': '2020013006215459919015339', 
            'refund_account_0': 'REFUND_SOURCE_UNSETTLED_FUNDS', 
            'refund_channel_0': 'ORIGINAL', 'refund_count': '1', 'refund_fee': '1', 
            'refund_fee_0': '1', 'refund_id_0': '50300103212020013014432993790', 
            'refund_recv_accout_0': '支付用户的零钱', 'refund_status_0': 'SUCCESS', 
            'refund_success_time_0': '2020-01-30 06:22:38', 'result_code': 'SUCCESS', 
            'return_code': 'SUCCESS', 'return_msg': 'success', 
            'sign': '78A32A1FC6CDACE55832D27173F19355', 'total_fee': '1', 
            'transaction_id': '4200000493202001306961376337'}
            """
            if response["refund_status_0"] == "SUCCESS":
                return {"status": "SUCCESS", "tip": "退款成功"}
            if response["refund_status_0"] == "REFUNDCLOSE":
                return {"status": "REFUNDCLOSE", "tip": "退款关闭"}
            if response["refund_status_0"] == "PROCESSING":
                return {"status": "PROCESSING", "tip": "退款处理中"}
            if response["refund_status_0"] == "CHANGE":
                return {"status": "CHANGE",
                        "tip": "退款异常，退款到银行发现用户的卡作废或者冻结了，导致原路退款银行卡失败。"}
            return {"status": "FAIL", "tip": "退款状态未知," + response["refund_status_0"]}
        else:
            """
            失败返回：
            {'code': 'FAIL', 
            'desc': 'out_refund_no,out_trade_no,transaction_id,refund_id is empty'}
            """
            return {"status": "FAIL", "tip": response["desc"]}


# # 微信回调
# @app.route('/wxpay_recall', methods=['POST','GET'])
def wxpay_recall():
    # 获取请求数据
    # 请求数据 = request.data.decode('utf-8')
    # 请求数据 = json.loads(请求数据, encoding='utf-8')
    # #
    # print(request)
    # print(请求数据)

    return 'ok'


if __name__ == '__main__':
    # 申请退款(100, 200, "123123")
    xx = 支付服务_小程序.查询退款("2020013006215459919015339")
    print(xx)
