from fastapi import FastAPI, Request
import uvicorn
import asyncio
import json
import base64
import datetime
import binascii
import datetime

app = FastAPI()
是否触发识别 = True


@app.post("/car/lcd")
async def 串口触发(data: Request):
    print("串口触发：",datetime.datetime.now(),"  ",await data.json())
    return "ok"


@app.post("/car/comet")
async def 轮询(data: Request):
    global 是否触发识别
    await asyncio.sleep(3)
    if 是否触发识别:
        return {"Response_AlarmInfoPlate": {"manualTrigger": "ok"}} # 回复 ok 进行手动触发
    else:
        return "ok"


@app.post("/car/getCarInfo")
async def 接受识别结果(data: Request):
    global 是否触发识别
    if not 是否触发识别:
        print("非手动触发结果")
        return "ok"
    else:
        是否触发识别 = False
    #
    res = await data.json()
    车牌号 = res["AlarmInfoPlate"]["result"]["PlateResult"]["license"]
    base64照片 = res["AlarmInfoPlate"]["result"]["PlateResult"]["imageFile"]
    拍摄时间dict = res["AlarmInfoPlate"]["result"]["PlateResult"]["timeStamp"]["Timeval"]
    拍摄时间str = "{decyear}{decmon:02d}{decday:02d}{dechour:02d}{decmin:02d}{decsec:02d}".format(**拍摄时间dict)
    车牌位置 = res["AlarmInfoPlate"]["result"]["PlateResult"]["location"]["RECT"]

    # 保存照片
    with open('imageFile/{}-{}.jpg'.format(拍摄时间str, 车牌号), 'wb') as imageFile:
        imgdata = base64.b64decode(base64照片)
        imageFile.write(imgdata)

    # BB88 AA 00                20150707 20150707 00 FF 33
    # BB88 AA 00 00413132333435 20150707 20150707 00 FF 33
    # 车牌号 00 41 31 32 33 34 35
    串口发送内容 = "BB88AA0000413132333435201507072015070700FF33"
    串口发送内容b64 = base64.b64encode(串口发送内容.encode("utf-8"))

    # 返回值
    if 车牌号 != "_无_":
        return {
            # Response_AlarmInfoPlate   Response_SerialData
            "Response_AlarmInfoPlate":
                {
                    "info": "ok",  # 回复ok开闸
                    "manualTigger": "ok",  # 回复 ok 进行手动触发
                    "is_pay": "true",
                    # 回复串口数据可以发送到相应串口
                    "serialData": [
                        # {"serialChannel": 0,
                        #  "data": 串口发送内容b64,
                        #  "dataLen": len(串口发送内容) / 2
                        #  },
                        {"serialChannel": 0,
                         "data": "AGT//+FBAQAACgAAAAAAAAAAABQLgAEAAAAAAAAAAAAAAAAAAABodHRwOi8vd3d3LmJhaWR1LmNvbQBwbGVhc2Ugc2NhbgDVJA==",
                         "dataLen": 73},

                    ],  # 数据1，可以有或者没有，收到后将发送到对应串口
                    # 白名单操作
                    # "white_list_operate":
                    #     {
                    #         "operate_type": 0,
                    #         "white_list_data": [
                    #             {"plate": 车牌号, "enable": 1, "need_alarm": 0,
                    #              "enable_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    #              "overdue_time": (datetime.datetime.now() + datetime.timedelta(days=1)).strftime(
                    #                  "%Y-%m-%d %H:%M:%S")}
                    #         ]
                    #     },
                },
        }
    else:
        data = "0064FFFFE13A0100000A0000000000000000000D0B80010000000000000000000000000000007777772E62616964752E636F6D00706C65617365207363616E00190D"
        dataB64 = "MDA2NEZGRkZFMTNBMDEwMDAwMEEwMDAwMDAwMDAwMDAwMDAwMDAwRDBCODAwMTAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDc3Nzc3NzJFNjI2MTY5NjQ3NTJFNjM2RjZEMDA3MDZDNjU2MTczNjUyMDczNjM2MTZFMDAxOTBE"
        print("无牌车")

        return {"Response_SerialData": {
            "info": "ok",           # 回复ok开闸
            "channelNum":0,         # 回复开闸端口号，若无，则默认为0
            "manualTigger": "ok",   # 回复 ok 进行手动触发
            # 回复串口数据可以发送到相应串口
            "serialData": [
                {"serialChannel": 0, "data": "AGT//+FBAQAACgAAAAAAAAAAABQLgAEAAAAAAAAAAAAAAAAAAABodHRwOi8vd3d3LmJhaWR1LmNvbQBwbGVhc2Ugc2NhbgDVJA==","dataLen": 73},
            ],  # 数据1，可以有或者没有，收到后将发送到对应串口
        }}


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8001, debug=False)
