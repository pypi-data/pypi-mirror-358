import httpx

SEND_MESSAGE_URL = (
    'https://api.weixin.qq.com/cgi-bin/message/subscribe/send'
    '?access_token={access_token}'
)


async def send_messages(access_token, 消息模板: dict):
    send_message_url = SEND_MESSAGE_URL.format(access_token=access_token)
    async with httpx.AsyncClient() as session:
        resp = await session.post(send_message_url, json=消息模板)

    retdict = resp.json()
    return retdict
