# -*- coding: utf-8 -*-
'http://commodity-image.oss-cn-shanghai.aliyuncs.com/logo168x168.png?x-oss-process=style/origin'

import oss2

accessKeyID = '见阿里云控制台'
accessKeySecret = '见阿里云控制台'
endpoint = 'oss-cn-shanghai.aliyuncs.com'  # 假设你的Bucket处于杭州区域
bucket名 = 'commodity-image'

'''
***************基本功能***************
'''

auth = oss2.Auth(accessKeyID, accessKeySecret)

bucket = oss2.Bucket(auth, endpoint, bucket名)

# 打开jpg文件
path = 'logo.jpg'
jpg = open(path, mode='r')

# Bucket中的文件名（key）为story.txt
key = 'logo'

# 上传
bucket.put_object(key, jpg.buffer)

# 下载
bucket.get_object(key).read()

# 删除
# __bucket.delete_object(key)

# 遍历Bucket里所有文件
for object_info in oss2.ObjectIterator(bucket):
    print(object_info.key)
