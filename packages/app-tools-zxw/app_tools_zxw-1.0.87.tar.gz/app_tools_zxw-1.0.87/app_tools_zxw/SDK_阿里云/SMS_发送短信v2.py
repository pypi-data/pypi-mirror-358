# pip install alibabacloud_dysmsapi20170525==3.0.0
import json
from alibabacloud_dysmsapi20170525.client import Client as Dysmsapi20170525Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dysmsapi20170525 import models as dysmsapi_20170525_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient
from enum import Enum


class 短信模板enum:
    验证码: str = "SMS_168725021"
    接单通知: str = "SMS_168725110"


class SMS阿里云:
    def __init__(self, accessKeyId, accessSecret):
        self.client = self.create_client(accessKeyId, accessSecret)

    @staticmethod
    def create_client(accessKeyId, accessSecret) -> Dysmsapi20170525Client:
        """
        使用AK&SK初始化账号Client
        @return: Client
        @throws Exception
        """
        config = open_api_models.Config(
            access_key_id=accessKeyId,
            access_key_secret=accessSecret
        )
        # Endpoint 请参考 https://api.aliyun.com/product/Dysmsapi
        config.endpoint = f'dysmsapi.aliyuncs.com'
        return Dysmsapi20170525Client(config)

    def 发送_验证码(self, 手机号: str,
                    验证码: str,
                    短信模板: str = 短信模板enum.验证码,
                    短信签名: str = "景募") -> None:
        send_sms_request = dysmsapi_20170525_models.SendSmsRequest(
            sign_name=短信签名,
            template_code=短信模板,
            phone_numbers=手机号,
            template_param=json.dumps({"code": 验证码})
        )
        runtime = util_models.RuntimeOptions()
        try:
            # 复制代码运行请自行打印 API 的返回值
            self.client.send_sms_with_options(send_sms_request, runtime)
        except Exception as error:
            # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
            # 错误 message
            print(error.message)
            # 诊断地址
            print(error.data.get("Recommend"))
            UtilClient.assert_as_string(error.message)

    async def 发送_验证码_async(self, 手机号: str,
                                验证码: str,
                                短信模板: str = 短信模板enum.验证码,
                                短信签名: str = "景募") -> None:
        send_sms_request = dysmsapi_20170525_models.SendSmsRequest(
            sign_name=短信签名,
            template_code=短信模板,
            phone_numbers=手机号,
            template_param=json.dumps({"code": 验证码})
        )
        runtime = util_models.RuntimeOptions()
        try:
            # 复制代码运行请自行打印 API 的返回值
            await self.client.send_sms_with_options_async(send_sms_request, runtime)
        except Exception as error:
            # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
            # 错误 message
            print(error.message)
            # 诊断地址
            print(error.data.get("Recommend"))
            UtilClient.assert_as_string(error.message)


if __name__ == '__main__':
    SMS阿里云("..", "..").发送_验证码('17512541044', "12345")
