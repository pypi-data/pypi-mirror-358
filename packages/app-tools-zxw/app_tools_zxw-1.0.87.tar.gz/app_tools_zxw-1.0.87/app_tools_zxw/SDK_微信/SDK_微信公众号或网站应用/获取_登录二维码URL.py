"""
# File       : 获取_登录二维码URL.py
# Time       ：2024/8/22 09:09
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
import urllib.parse
from app_tools_zxw.configs import WeChatPub


def get_qrcode_url(WECHAT_REDIRECT_URI, WECHAT_SCOPE="snsapi_login") -> str:
    # 构造微信二维码登录URL
    encoded_redirect_uri = urllib.parse.quote(WECHAT_REDIRECT_URI)
    qr_code_url = (
        f"https://open.weixin.qq.com/connect/qrconnect?"
        f"appid={WeChatPub.app_id}&"
        f"redirect_uri={encoded_redirect_uri}&"
        f"response_type=code&"
        f"scope={WECHAT_SCOPE}&"
        f"state={WeChatPub.state}#wechat_redirect"
    )
    return qr_code_url
