"""
# File       : api_服务器配置验证.py
# Time       ：2024/8/21 上午5:18
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
import hashlib
from fastapi import APIRouter, Response
from app_tools_zxw.Errors.api_errors import HTTPException_AppToolsSZXW
from config import WeChatPub

router = APIRouter(prefix="/wechat")


def check_signature(signature: str, timestamp: str, nonce: str) -> bool:
    """
    验证微信签名
    --------------------------
    signature 微信加密签名，signature结合了开发者填写的token参数和请求中的timestamp参数、nonce参数。
    timestamp 时间戳
    nonce 随机数
    echostr 随机字符串

    开发者通过检验signature对请求进行校验（下面有校验方式）。
    若确认此次GET请求来自微信服务器，请原样返回echostr参数内容，则接入生效，成为开发者成功，否则接入失败。
    加密/校验流程如下：
        1）将token、timestamp、nonce三个参数进行字典序排序
        2）将三个参数字符串拼接成一个字符串进行sha1加密
        3）开发者获得加密后的字符串可与signature对比，标识该请求来源于微信
    """
    token = WeChatPub.接口配置信息_Token
    # 将 token, timestamp, nonce 排序并拼接成字符串
    data = ''.join(sorted([token, timestamp, nonce]))
    # 使用 SHA1 算法加密
    sha1 = hashlib.sha1()
    sha1.update(data.encode('utf-8'))
    hashcode = sha1.hexdigest()
    # 判断 hashcode 是否与 signature 一致
    return hashcode == signature


@router.get("/verify")
async def wechat_verify(signature: str, timestamp: str, nonce: str, echostr: str):
    """微信公众号服务器验证"""
    # 校验签名
    if check_signature(signature, timestamp, nonce):
        return Response(content=echostr)
    else:
        raise HTTPException_AppToolsSZXW(error_code=1015,
                                         http_status_code=403,
                                         detail="Signature verification failed")


if __name__ == '__main__':
    signature = 'fc7017c67559cc25acffb96f302641ff8e8b5af1'
    echostr = '3894841337193693150'
    timestamp = '1724210780'
    nonce = '672323842'

    res = check_signature(signature, timestamp, nonce)
    print(res)
