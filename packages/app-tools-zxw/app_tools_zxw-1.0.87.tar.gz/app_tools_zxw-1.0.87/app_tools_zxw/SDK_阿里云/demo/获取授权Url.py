from aliyunsdkcore import client
from aliyunsdksts.request.v20150401 import AssumeRoleRequest
import json
import oss2
import time

'''
***************高级功能***************
###
### 使用STS进行临时授权
STS应用完整的示例代码请参见GitHub。
您可以通过STS（Security Token Service）进行临时授权访问。更多有关STS的内容请参见访问控制API参考（STS）中的简介。
关于账号及授权的详细信息请参见最佳实践中的STS临时授权访问。
首先您需要安装官方的Python STS客户端：pip install aliyun-python-sdk-sts
'''

accessKeyID = '见本地文件'
accessKeySecret = '见本地文件'
endpoint = 'oss-cn-shanghai.aliyuncs.com'  # 假设你的Bucket处于杭州区域
bucket名 = '见本地文件'
# role_arn是角色的资源名称。
RoleArn = 'acs:ram::1314717226629429:role/aliyunosstokengeneratorrole'
RoleSessionName = 'external-username'
DurationSeconds = 3600

# 阿里云主账号AccessKey拥有所有API的访问权限，风险很高。
# 强烈建议您创建并使用RAM账号进行API访问或日常运维，请登录 https://ram.console.aliyun.com 创建RAM账号。
clt = client.AcsClient(accessKeyID, accessKeySecret, 'cn-hangzhou')
req = AssumeRoleRequest.AssumeRoleRequest()
print(req.get_url('shanghai', accessKeyID, accessKeySecret))

# 设置返回值格式为JSON。
req.set_accept_format('json')
req.set_RoleArn(RoleArn)
req.set_RoleSessionName('session-name')
body = clt.do_action_with_exception(req)
# print(body)
# 使用RAM账号的AccessKeyId和AccessKeySecret向STS申请临时token。
token = json.loads(body)

# 使用临时token中的认证信息初始化StsAuth实例。
auth = oss2.StsAuth(token['Credentials']['AccessKeyId'],
                    token['Credentials']['AccessKeySecret'],
                    token['Credentials']['SecurityToken'])
# print(__auth.__auth())
# 使用StsAuth实例初始化存储空间。
bucket = oss2.Bucket(auth, endpoint, bucket名)

# 上传一个字符串。
bucket.put_object('object-name.txt', b'hello world')

# 上传图片，方法一
# with open('logo.jpg', 'rb') as f:
#     __bucket.put_object('logo11.jpg', f)

'''  
#######  使用签名Url上传文件  #######  
'''
# 生成请求Url
url = bucket.sign_url(method='PUT', key='logo444.jpg', expires=8)
url2 = bucket.sign_url(method='GET', key='xxxxx.jpg', expires=8)

print(url2)
# 上传图片，方法二
# __bucket.put_object_with_url_from_file(url,'logo.jpg')

# 上传图片，方法三
# time.sleep(10)
import requests

print(url)
res = requests.request('POST', url, data=open('logo.jpg', 'rb'))
print(res.headers)
