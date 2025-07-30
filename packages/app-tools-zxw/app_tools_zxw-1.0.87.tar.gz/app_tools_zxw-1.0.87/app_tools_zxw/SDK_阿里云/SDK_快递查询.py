import urllib.request
import ssl
from urllib.parse import quote
import string
import httpx

host = 'https://wuliu.market.alicloudapi.com'
path = '/kdi'
method = 'GET'
appcode = ''


def query(no="780098068058", type="zto") -> str:
    querys = 'no=%s&type=%s' % (no, type)
    bodys = {}
    url = host + path + '?' + querys
    newurl = quote(url, safe=string.printable)
    #
    request = urllib.request.Request(newurl)
    request.add_header('Authorization', 'APPCODE ' + appcode)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    response = urllib.request.urlopen(request, context=ctx)
    content = response.read()
    if content:
        return content.decode('UTF-8')
    else:
        return ""


async def async_query(no="780098068058", type="zto") -> str:
    querys = 'no=%s&type=%s' % (no, type)
    bodys = {}
    url = host + path + '?' + querys
    newurl = quote(url, safe=string.printable)
    #
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    #
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(newurl, headers={"Authorization": 'APPCODE ' + appcode}, timeout=30)
    #
    content = response.content
    #
    if content:
        return content.decode('utf-8')
    else:
        return ""


def 整理输出所有快递公司(path="ExpressInfo.csv"):
    import pandas as pd
    data = pd.read_csv(path)
    for i in range(len(data.index)):
        item = data.iloc[i, :]
        print("'%s':'%s'," % (item[0], item[1]))


if __name__ == '__main__':
    a = query()
    print(a)

    整理输出所有快递公司()
