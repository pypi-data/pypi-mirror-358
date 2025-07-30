from pydantic import BaseModel


class model模板消息内容(BaseModel):
    模板id: str = "lzOT9K5cf5lNh1cvdCx2h40C2PixGnZyWaCC0Q6bH9M"
    订单编号: str = " "
    商品信息: str = " "
    快递公司: str = " "
    快递单号: str = " "
    收货地址: str = " "


def 生成消息模板_发货提醒(openid, data: model模板消息内容) -> dict:
    收货地址 = data.收货地址
    if len(收货地址) > 20:
        收货地址 = 收货地址[0:17] + "..."
    d = {
        'touser': openid,
        'template_id': data.模板id,
        # page -> project uri
        'page': 'index',
        'miniprogram_state': 'developer',
        'lang': 'zh_CN',
        'data': {
            'number1': {'value': data.订单编号},
            'thing7': {'value': data.商品信息},
            'name3': {'value': data.快递公司},
            'character_string4': {'value': data.快递单号},
            'thing8': {'value': 收货地址}
        }
    }
    print("待发送的模板消息 = ", d)
    return d
