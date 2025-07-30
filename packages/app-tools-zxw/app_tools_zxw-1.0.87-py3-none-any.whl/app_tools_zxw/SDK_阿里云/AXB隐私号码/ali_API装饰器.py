"""
# File       : ali_API装饰器.py
# Time       ：2022/8/17 05:35
# Author     ：xuewei zhang(张薛伟)
# Email      ：307080785@qq.com
# version    ：python 3.9
# Description：
"""
from typing import Any
from Tea.model import TeaModel
from functools import wraps
from pydantic import BaseModel
from decohints import decohints
import json


class ResBaseModel(BaseModel):
    Code: str
    Message: str
    RequestId: str = ""
    data: Any = ""


@decohints
def ali_api_process(ali_api_func):
    """
    阿里api调用函数返回值统一整理
    :param ali_api_func: 阿里api调用函数,需规定返回值为: (请求是否成功,返回数据)
            注意:请求是否成功 仅指api调用是否报错
    :return:
    """

    @wraps(ali_api_func)
    async def wrap_func(*args, **kwargs) -> ResBaseModel:
        res = await ali_api_func(*args, **kwargs)
        # res为TeaModel类型说明API请求成功
        if isinstance(res, TeaModel):
            # 整理 基本返回值 以外的数据,放在data字段里
            res: dict = res.body.to_map()
            data: dict = {}
            for key, value in res.items():
                if key not in ["Code", "Message", "RequestId"]:
                    data[key] = value
            return ResBaseModel(data=data, **res)
        # API请求发生错误
        elif isinstance(res, Exception):
            return ResBaseModel(**{"Code": "api响应错误error", "Message": str(kwargs.get("error")), "data": str(res)})

    return wrap_func


@decohints
def ali_api_process_旧版(ali_api_func):
    """
    阿里api调用函数返回值统一整理
    :param ali_api_func: 阿里api调用函数,需规定返回值为: (请求是否成功,返回数据)
            注意:请求是否成功 仅指api调用是否报错
    :return:
    """

    @wraps(ali_api_func)
    def wrap_func(*args, **kwargs) -> ResBaseModel:
        response: bytes = ali_api_func(*args, **kwargs)
        if isinstance(response, Exception):
            # API请求发生错误
            return ResBaseModel(**{"Code": "api响应错误error", "Message": str(kwargs.get("error")),"data": str(response)})
        else:
            res = json.loads(response.decode())
            return ResBaseModel(**res)

    return wrap_func
