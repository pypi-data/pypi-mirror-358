"""
# File       : returnModel.py
# Time       ：2022/8/16 08:35
# Author     ：xuewei zhang(张薛伟)
# Email      ：307080785@qq.com
# version    ：python 3.9
# Description：
"""
from pydantic import BaseModel


class resModel(BaseModel):
    Code: str
    Message: str

