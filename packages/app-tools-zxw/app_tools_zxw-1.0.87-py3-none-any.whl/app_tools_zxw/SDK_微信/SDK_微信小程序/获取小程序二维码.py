import json
import numpy as np
from PIL import Image
from io import BytesIO
import httpx

'''
小程序码文档说明：
https://developers.weixin.qq.com/miniprogram/dev/api-backend/open-api/qr-code/wxacode.getUnlimited.html
'''

baseUrl = 'https://api.weixin.qq.com/wxa/getwxacodeunlimit?access_token='

import sys


async def get小程序二维码(commerceID, tableID, wxAccessToken):
    postData = {
        'page': 'pages/index/index',
        'scene': 'id=%s&no=%s' % (str(commerceID), str(tableID)),  # 商户ID与桌号，-1代表外送订单
        'width': 280,  # 二维码大小
        'auto_color': False,  # 线条是否自动颜色
        'line_color': {"r": 0, "g": 0, "b": 0},  #
        'is_hyaline': False  # 底色是否透明
    }
    postUrl = baseUrl + wxAccessToken

    # 获取小程序二维码
    async with httpx.AsyncClient() as client:
        re = await client.post(postUrl, data=postData)
    图片二进制数据 = re.content

    # 读取成数组
    imageBytes = BytesIO(图片二进制数据)

    #
    print("图片大小 = ", sys.getsizeof(imageBytes) / 1024, "KB")

    return imageBytes


def 读取成图片对象(图片二进制数据):
    image = Image.open(BytesIO(图片二进制数据))
    array = np.array(image).tolist()
    return image


def 图片转化为Bytes(image):
    imageBytes = BytesIO()
    image.save(imageBytes, format='JPEG')
    return imageBytes


if __name__ == '__main__':
    data = get小程序二维码(commerceID='dads', tableID=-1, wxAccessToken="...")
    # plt.imshow(data)
    # plt.show()
