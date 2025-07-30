"""
# File       : oss_async.py
# Time       ：2024/9/1 下午6:18
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
import asyncio
import oss2
from oss2.models import PutObjectResult
from oss2.exceptions import OssError


class AsyncAliyunOSS:
    def __init__(self, access_key_id, access_key_secret, endpoint, bucket_name):
        self.auth = oss2.Auth(access_key_id, access_key_secret)
        self.bucket = oss2.Bucket(self.auth, endpoint, bucket_name)

    async def upload_file(self, local_file_path, oss_file_path):
        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(
                None, self.bucket.put_object_from_file, oss_file_path, local_file_path
            )
            if isinstance(result, PutObjectResult):
                return f"File uploaded successfully. ETag: {result.etag}"
            else:
                return "File upload failed."
        except OssError as e:
            return f"OSS error occurred: {str(e)}"
        except Exception as e:
            return f"An error occurred: {str(e)}"

    async def get_download_url(self, oss_file_path, expiration=3600):
        loop = asyncio.get_event_loop()
        try:
            url = await loop.run_in_executor(
                None, self.bucket.sign_url, 'GET', oss_file_path, expiration
            )
            print(url)
            return url
        except OssError as e:
            return f"OSS error occurred: {str(e)}"
        except Exception as e:
            return f"An error occurred: {str(e)}"


async def main():
    # 使用示例
    oss_client = AsyncAliyunOSS(
        access_key_id=AliyunOSS.access_key_id,
        access_key_secret=AliyunOSS.access_key_secret,
        endpoint=AliyunOSS.endpoint外网,
        bucket_name=AliyunOSS.bucket_name
    )

    # 上传文件
    upload_result = await oss_client.upload_file('/Users/zhangxuewei/Documents/GitHub/myProj/个人_自动教案生成/rq.txt',
                                                 '中国/rq.txt')
    print("upload_result: ", upload_result)

    # 获取下载链接
    download_url = await oss_client.get_download_url('中国/rq.txt')
    print(f"Download URL: {download_url}")


if __name__ == "__main__":
    from config import AliyunOSS
    asyncio.run(main())
