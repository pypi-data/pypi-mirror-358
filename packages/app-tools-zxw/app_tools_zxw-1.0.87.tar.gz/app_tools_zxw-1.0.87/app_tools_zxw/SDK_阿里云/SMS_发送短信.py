from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
import json

from enum import Enum


class 短信模板enum(str, Enum):
    验证码: str = "SMS_168725021"
    接单通知: str = "SMS_168725110"


class SMS阿里云:
    userID = 'sms@.onaliyun.com'

    def __init__(self, accessKeyId, accessSecret):
        self.client = AcsClient(accessKeyId, accessSecret, 'cn-hangzhou')

    def 发送短信验证码SMS(self, 手机号: str,
                          验证码: str,
                          短信模板: str = 短信模板enum.验证码,
                          短信签名: str = "景募"):
        """
        return: {
            'Message': '触发小时级流控Permits:5',
            'RequestId': 'E3F11903-3F92-4245-8FDD-407BAE980FCA',
            'Code': 'isv.BUSINESS_LIMIT_CONTROL'
        }
        """
        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain('dysmsapi.aliyuncs.com')
        request.set_method('POST')
        request.set_protocol_type('https')  # https | http
        request.set_version('2017-05-25')
        request.set_action_name('SendSms')

        request.add_query_param('RegionId', "cn-hangzhou")
        request.add_query_param('PhoneNumbers', 手机号)
        request.add_query_param('SignName', 短信签名)
        request.add_query_param('TemplateCode', 短信模板)
        request.add_query_param('TemplateParam', "{\"code\":%s}" % 验证码)

        #
        response = self.client.do_action_with_exception(request)
        re = json.loads(response.decode('utf-8'))
        #
        return re


if __name__ == '__main__':
    sms = SMS阿里云('...', '...')
    re = sms.发送短信验证码SMS('17512541044', "12345")
    print(re)
