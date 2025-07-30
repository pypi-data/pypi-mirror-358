import base64

print(base64.b64encode(b"13905233066"))

cmd忙碌 = {
    "cmd": "set_led_show",
    "id": "12365",
    "body": {
        "led_enable": 1,
        "led_content": {
            "led_proto": 3,
            "led_status": 1,
            "led_refresh_time": 5,
            "led_line_num": 4,
            "line_content": [
                {"show_mode": 1, "show_content": base64.b64encode("苏H1358K".encode()).decode()},
                {"show_mode": 1, "show_content": base64.b64encode("手机0066".encode()).decode()},
                {"show_mode": 1, "show_content": base64.b64encode("手机0066".encode()).decode()},
                {"show_mode": 1, "show_content": base64.b64encode("手机0066".encode()).decode()},
            ],
        },
        "voice_mode": 0x20,
        "voice_content": {
            "voice_volume": 1,
            "voice_welcom": 1,
            "voice_tag": 1,
            "play_content": "6IuPMTM1OEs="
        },
        "car_info": {
            "park_time": 32,
            "payment_amount": 90,
            "car_type": 2,
            "car_plate": "001358K"
        }
    }
}

cmd空闲 = {
    "cmd": "set_led_show",
    "id": "12365",
    "body": {
        "led_enable": 1,
        "led_content": {
            "led_proto": 3,
            "led_status": 1,
            "led_refresh_time": 15,
            "led_line_num": 4,
            "line_content": [
                {"show_mode": 0x02, "show_content": base64.b64encode("苏H1358K".encode()).decode()},
                {"show_mode": 1, "show_content": base64.b64encode("秀山石材".encode()).decode()},
                {"show_mode": 1, "show_content": base64.b64encode("秀山石材".encode()).decode()},
                {"show_mode": 1, "show_content": base64.b64encode("秀山石材".encode()).decode()}
            ],
        },
        "voice_mode": 0x40,
        "voice_content": {
            "voice_volume": 1,
            "voice_welcom": 1,
            "voice_tag": 1,
            "play_content": "57KkQjEyMzQ1NuitpizmrKLov47lhYnkuLQs6K+35YWl5Zy65YGc6L2mLOWBnOi9pjMw5YiGLOivt+S6pOi0uTEw5YWDLOS4gOi3r+W5s+WuiQ=="
        },
        "car_info": {
            "park_time": 32,
            "payment_amount": 90,
            "car_type": 2,
            "car_plate": "001358K"
        }
    }
}


def __cmd生成(cmd: str, id: str = "1"):
    return {"cmd": cmd, "id": id}


cmd获取屏显文字 = {"cmd": "get_led_show", "id": "12365"}
cmd获取显示屏串口号 = {"cmd": "get_led_serial_port"}
cmd手动触发识别 = {"cmd": "trigger"}

cmd最近一次识别结果 = {"cmd": "getivsresult", "image": True, "format": "json"}
cmd获取视频播放uri = __cmd生成("get_rtsp_uri", "123")
