"""
# File       : AXB_解除绑定.py
# Time       ：2022/8/16 05:49
# Author     ：xuewei zhang(张薛伟)
# Email      ：307080785@qq.com
# version    ：python 3.9
# Description：
"""
from typing import Union
import datetime
from alibabacloud_dyplsapi20170525.client import Client as Dyplsapi20170525Client
from alibabacloud_dyplsapi20170525 import models as dyplsapi_20170525_models
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_util import models as util_models
from pydantic import BaseModel, Field
from app_tools_zxw.SDK_阿里云.AXB隐私号码.ali_API装饰器 import ali_api_process, ResBaseModel


class AXB_绑定与解绑:
    def __init__(self, access_key_id: str, access_key_secret: str):
        """
        使用AK&SK初始化账号Client
        @param access_key_id:
        @param access_key_secret:
        @throws Exception
        """
        config = open_api_models.Config(
            # 您的 AccessKey ID,
            access_key_id=access_key_id,
            # 您的 AccessKey Secret,
            access_key_secret=access_key_secret
        )
        # 访问的域名
        config.endpoint = f'dyplsapi.aliyuncs.com'
        # 客户端
        self.client = Dyplsapi20170525Client(config)

    @ali_api_process
    async def 绑定(self, pool_key: str, phone_no_a: str, phone_no_b: str, expiration: Union[str, int],
                 expect_city: Union[str, None] = None, is_recording_enabled: bool = False,
                 phone_no_x: Union[str, None] = None):
        """
        绑定手机号
        :param pool_key:   号码池key       - demo: 'FC100000159944414'
        :param phone_no_a: 待绑定手机号码1
        :param phone_no_b: 待绑定手机号码2
        :param phone_no_x: 指定隐私号码,如果为None,则ali智能选定
        :param expiration: 绑定结束日期
                            - 当类型为str时,代表截止日期字符串 :demo: '2022-08-15 20:40:00'
                            - 当类型为int时,代表从现在算起,绑定的秒数
        :param expect_city: 可选- 选定隐私号码归属地 - demo: '郑州'
        :param is_recording_enabled:可选- 是否录音

        :return:
                {'Code': 'OK', 'Message': 'OK', 'RequestId': '557CF0EF-F417-549C-93FA-97CE6C1F9C50',
                 'SecretBindDTO': {'Extension': '17512541044', 'SecretNo': '17148115358',
                 'SubsId': '1000068102552039'}}
        """
        # 计算截止日期
        expiration = self.__cal_到期时间(expiration)
        # 整理请求
        bind_axb_request = dyplsapi_20170525_models.BindAxbRequest(
            pool_key=pool_key,
            phone_no_a=phone_no_a,
            phone_no_b=phone_no_b,
            phone_no_x=phone_no_x,
            expiration=expiration,
            expect_city=expect_city,
            is_recording_enabled=is_recording_enabled
        )
        runtime = util_models.RuntimeOptions()
        try:
            return await self.client.bind_axb_with_options_async(bind_axb_request, runtime)
        except Exception as error:
            return error

    @ali_api_process
    async def 解绑(self, pool_key: str, secret_no: str, subs_id: str):
        """
        解绑手机号
        :param pool_key: 号码池key - demo: 'FC100000159944414'
        :param secret_no: 隐私号码 - demo: '17148117736'
        :param subs_id: SubsId绑定关系ID - demo: ''
        :return:
        """
        unbind_subscription_request = dyplsapi_20170525_models.UnbindSubscriptionRequest(
            pool_key=pool_key,
            secret_no=secret_no,
            subs_id=subs_id
        )
        runtime = util_models.RuntimeOptions()
        try:
            res = await self.client.unbind_subscription_with_options_async(unbind_subscription_request, runtime)
            return res
        except Exception as error:
            return error

    @ali_api_process
    async def 修改绑定(self, subs_id: str, phone_no_x: str, operate_type: str, pool_key: str,

                   phone_no_a: str = None, phone_no_b: str = None, expiration: str = None):
        """
        :param subs_id: SubsId绑定关系ID - demo: ''
        :param operate_type:修改绑定关系的操作。取值：updateNoA：修改A号码。
                                                  updateNoB：修改B号码。
                                                  updateExpire：修改绑定关系有效期。
                                                  updateAxgGroup：修改G号码组。
                                                  updateCallRestrict：设置单通呼叫限制。
                                                  updateCallDisplayType：更新呼叫显号逻辑。
                                                  updateOutId：更新OutId字段。
                                                  updateIsRecordingEnabled：更新绑定中录音状态。
        :param pool_key: 号码池key - demo: 'FC100000159944414'
        :param phone_no_a: 待绑定手机号码1
        :param phone_no_b: 待绑定手机号码2
        :param phone_no_x: 指定隐私号码,如果为None,则ali智能选定
        :param expiration: 绑定结束日期
                            - 当类型为str时,代表截止日期字符串 :demo: '2022-08-15 20:40:00'
                            - 当类型为int时,代表从现在算起,绑定的秒数
        :return:ResBaseModel
        """
        update_subscription_request = dyplsapi_20170525_models.UpdateSubscriptionRequest(
            pool_key=pool_key,
            subs_id=subs_id,
            phone_no_x=phone_no_x,
            phone_no_a=phone_no_a,
            phone_no_b=phone_no_b,
            operate_type=operate_type,
            expiration=self.__cal_到期时间(expiration)
        )
        runtime = util_models.RuntimeOptions()
        try:
            return await self.client.update_subscription_with_options_async(update_subscription_request, runtime)
        except Exception as error:
            return error

    @staticmethod
    def __cal_到期时间(expiration: Union[int, str]):
        if isinstance(expiration, int):
            expiration = datetime.datetime.now() + datetime.timedelta(seconds=expiration)
            expiration = expiration.strftime("%Y-%m-%d %H:%M:%S")
        return expiration

    @staticmethod
    def bind_情况校验(res_body: dict):
        """
        绑定手机号情况校验
        :param res_body: 绑定返回值 ,demo:
               {'Code': 'isv.EXPIRE_DATE_ILLEGAL', 'Message': 'expireDate less than 1 minutes from now', ...}
        :return:
        """
        status = {
            'OK': '成功',
            'isv.NO_AVAILABLE_NUMBER': '号码池可用号码不足',
            'isv.EXPIRE_DATE_ILLEGAL': '过期时间不正确'
        }
        return res_body.get("Code")


"""
    AXB_api 数据类型 定义
"""


class _AXB_绑定_返回值(BaseModel):
    Extension: str = Field(description="主号码")
    SecretNo: str = Field(description="隐私号码")
    SubsId: str = Field(description="绑定id")


class AXB_绑定_返回值(BaseModel):
    SecretBindDTO: _AXB_绑定_返回值


class AXB_修改绑定_operate_type:
    updateNoA = "updateNoA"  # ：修改A号码。
    updateNoB = "updateNoB"  # ：修改B号码。
    updateExpire = "updateExpire"  # ：修改绑定关系有效期。
    updateAxgGroup = "updateAxgGroup"  # ：修改G号码组。
    updateCallRestrict = "updateCallRestrict"  # ：设置单通呼叫限制。
    updateCallDisplayType = "updateCallDisplayType"  # ：更新呼叫显号逻辑。
    updateOutId = "updateOutId"  # ：更新OutId字段。
    updateIsRecordingEnabled = "updateIsRecordingEnabled"  # ：更新绑定中录音状态。


if __name__ == '__main__':
    from asyncio import run
    from comm公用配置.configs import ali_access_key_id, ali_access_key_secret, ali_secretNo_pool_key

    # 绑定
    axb_api = AXB_绑定与解绑(ali_access_key_id, ali_access_key_secret)
    xx: ResBaseModel = run(
        axb_api.绑定(pool_key=ali_secretNo_pool_key,
                   phone_no_a='17512541044',
                   phone_no_b='15050560029',
                   phone_no_x='17148117736',
                   expect_city='南京',
                   is_recording_enabled=True,
                   expiration=60 * 5)
    )
    if xx.Code == "OK":
        b_inf = AXB_绑定_返回值(**xx.data).SecretBindDTO
        print("绑定成功,res = ", b_inf.dict())
    else:
        raise ValueError("绑定失败")

    # 修改绑定
    res: ResBaseModel = run(axb_api.修改绑定(b_inf.SubsId, b_inf.SecretNo,
                                         AXB_修改绑定_operate_type.updateNoB,
                                         ali_secretNo_pool_key,
                                         phone_no_b="13852248788")
                            )
    print("修改绑定关系,res = ", res.dict())

    # 解除绑定
    # res = run(axb_api.解绑(ali_secretNo_pool_key, b_inf.SecretNo, b_inf.SubsId))
    # print("解除绑定,res = ", res)
