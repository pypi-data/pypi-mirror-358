import jpush
from jpush import common

app_key = "见本地文件"
master_secret = "见本地文件"
_jpush = jpush.JPush(app_key, master_secret)


def push_to_all(is生产环境=False):
    push = _jpush.create_push()
    # _jpush.set_logging("DEBUG")
    #
    push.audience = jpush.all_
    push.notification = jpush.notification(alert="hello python jpush api")
    push.platform = jpush.all_
    # 设施iOS推送环境
    push.options = {"apns_production": is生产环境}  # False 测试环境
    #
    try:
        response = push.send()
    except common.Unauthorized:
        raise common.Unauthorized("Unauthorized")
    except common.APIConnectionException:
        raise common.APIConnectionException("conn error")
    except common.JPushFailure:
        print("JPushFailure")
    except:
        print("Exception")


def push_to_别名(商户id, is生产环境=False, alert="您有新订单"):
    push = _jpush.create_push()
    #
    push.audience = jpush.alias(商户id)
    push.notification = jpush.notification(alert=alert)
    push.platform = jpush.all_
    # 设施iOS推送环境
    push.options = {"apns_production": is生产环境}  # False 测试环境
    #
    try:
        response = push.send()
        print("推送通知发送成功:", response)
    except common.Unauthorized:
        raise common.Unauthorized("Unauthorized")
    except common.APIConnectionException:
        raise common.APIConnectionException("conn error")
    except common.JPushFailure:
        print("JPushFailure")
    except:
        print("Exception")
