"""
# File       : AXB_查询与购买.py
# Time       ：2022/8/16 08:34
# Author     ：xuewei zhang(张薛伟)
# Email      ：307080785@qq.com
# version    ：python 3.9
# Description：
"""
from alibabacloud_dyplsapi20170525.client import Client as Dyplsapi20170525Client
from alibabacloud_dyplsapi20170525 import models as dyplsapi_20170525_models
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_util import models as util_models
from app_tools_zxw.SDK_阿里云.AXB隐私号码.ali_API装饰器 import ali_api_process


class AXB_查询购买释放:
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
    async def 可购余量查询(self, spec_id: int = 1, city: str = '全国列表'):
        """
        :param spec_id:号码类型。取值：1：虚商号码，即170或171。2：运营商号码。3：95号码。
        :param city:号码的归属地。
                    SpecId设置为1或2时，可以在参数City中指定查询
                    支持输入单个城市名称查询。
                    支持输入“全国”查询，可返回全国可购号码余量。
                    支持输入“全国列表”查询，将返回全国城市中有号码的城市及数量，无号码的城市不会返回。
                    SpecId设置为3时，95号码不区分归属地，只能查询全部95号码可购余量，即必须指定City为全国通用。
        :return:
                {
                    'Code': 'OK', 'Message': 'OK', 'RequestId': 'D333B290-6DB3-5BCA-A60B-37DAC059A1A3',
                    'SecretRemainDTO': {
                        'RemainDTOList': {'remainDTO': [{'Amount': 6, 'City': '上海'}]}
                    }
                }
        """
        query_secret_no_remain_request = dyplsapi_20170525_models.QuerySecretNoRemainRequest(
            spec_id=spec_id,
            city=city
        )
        runtime = util_models.RuntimeOptions()
        try:
            return await self.client.query_secret_no_remain_with_options_async(query_secret_no_remain_request, runtime)
        except Exception as error:
            return error

    @ali_api_process
    async def 购买号码(self, pool_key: str, spec_id: int = 1, city: str = '全国', display_pool: bool = False):
        """
        :param pool_key: 号码池Key。请登录号码隐私保护控制台，在号码池管理中查看号码池Key。
        :param spec_id:  号码类型。取值：1：虚商号码，即170或171。2：运营商号码。3：95号码。
        :param city:     号码的归属地。
                    SpecId设置为1或2时，可以在参数City中指定查询
                    支持输入单个城市名称查询。
                    支持输入“全国”查询，可返回全国可购号码余量。
                    支持输入“全国列表”查询，将返回全国城市中有号码的城市及数量，无号码的城市不会返回。
                    SpecId设置为3时，95号码不区分归属地，只能查询全部95号码可购余量，即必须指定City为全国通用。
        :param display_pool:是否将该号码置于显号池。- 该参数仅对开通显号功能的客户生效。
        :return:
            {'Code': 'OK', 'Message': 'OK', 'RequestId': '90C99F5A-726B-5974-8B9D-2453C79E90B7',
                 'SecretBuyInfoDTO': {'SecretNo': '17092147005'}}
        """
        buy_secret_no_request = dyplsapi_20170525_models.BuySecretNoRequest(
            pool_key=pool_key,
            spec_id=spec_id,
            city=city,
            display_pool=display_pool
        )
        runtime = util_models.RuntimeOptions()
        try:
            return await self.client.buy_secret_no_with_options_async(buy_secret_no_request, runtime)
        except Exception as error:
            return error

    @ali_api_process
    async def 释放号码(self, pool_key: str, secret_no: str):
        """
        :param pool_key: 号码池Key。请登录号码隐私保护控制台，在号码池管理中查看号码池Key。
        :param secret_no:指定号码前缀。购买号码时，如果指定SecretNo，会根据指定的号码前缀模糊匹配手机号。
                - 最长可设置18位号码前缀。
        :return:
           {'Code': 'OK', 'Message': 'OK', 'RequestId': 'BA34B781-DE73-58D6-AB69-BCD74A8E769C'}
        """
        release_secret_no_request = dyplsapi_20170525_models.ReleaseSecretNoRequest(
            pool_key=pool_key,
            secret_no=secret_no
        )
        runtime = util_models.RuntimeOptions()
        try:
            return await self.client.release_secret_no_with_options_async(release_secret_no_request, runtime)
        except Exception as error:
            return error


class AXB_Api返回Code:
    号码余量不足 = 'isv.NO_AVAILABLE_NUMBER'


if __name__ == '__main__':
    from asyncio import run
    from comm公用配置.configs import ali_access_key_id, ali_access_key_secret, ali_secretNo_pool_key

    # 绑定
    nn = AXB_查询购买释放(ali_access_key_id, ali_access_key_secret)
    xx: dict = run(
        nn.可购余量查询()
    )
    print("查询号码余量:", xx)

    #
    # xx = run(nn.购买号码(ali_secretNo_pool_key))
    # print("购买号码:", xx)
    #
    # #
    # phone = xx.data['SecretBuyInfoDTO']['SecretNo']
    # xx = run(nn.释放号码(ali_secretNo_pool_key, phone))
    # print("释放号码: ", xx)
