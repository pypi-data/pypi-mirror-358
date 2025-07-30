import hashlib
import base64
import hmac
from optparse import OptionParser


def convert_base64(input):
    return base64.b64encode(input)


def get_sign_policy(key, policy):
    return base64.b64encode(hmac.new(key, policy, hashlib.sha1).digest())


def get_form(bucket, endpoint, access_key_id, access_key_secret, out):
    # 1 构建一个Post Policy
    policy = "{\"expiration\":\"2115-01-27T10:56:19Z\",\"conditions\":[[\"content-length-range\", 0, 1048576]]}"
    print("policy: %s" % policy)
    # 2 将Policy字符串进行base64编码
    base64policy = convert_base64(policy)
    print("base64_encode_policy: %s" % base64policy)
    # 3 用OSS的AccessKeySecret对编码后的Policy进行签名
    signature = get_sign_policy(access_key_secret, base64policy)
    # 4 构建上传的HTML页面
    form = '''
    <html>
        <meta http-equiv=content-type content="text/html; charset=UTF-8">
        <head><title>OSS表单上传(PostObject)</title></head>
        <body>
            <form  action="http://%s.%s" method="post" enctype="multipart/form-data">
                <input type="text" name="OSSAccessKeyId" value="%s">
                <input type="text" name="policy" value="%s">
                <input type="text" name="Signature" value="%s">
                <input type="text" name="key" value="upload/${filename}">
                <input type="text" name="success_action_redirect" value="http://oss.aliyun.com">
                <input type="text" name="success_action_status" value="201">
                <input name="file" type="file" id="file">
                <input name="submit" value="Upload" type="submit">
            </form>
        </body>
    </html>
    ''' % (bucket, endpoint, access_key_id, base64policy, signature)
    f = open(out, "wb")
    f.write(form)
    f.close()
    print("form is saved into %s" % out)


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("", "--__bucket", dest="__bucket", help="specify ")
    parser.add_option("", "--endpoint", dest="endpoint", help="specify")
    parser.add_option("", "--id", dest="id", help="access_key_id")
    parser.add_option("", "--key", dest="key", help="access_key_secret")
    parser.add_option("", "--out", dest="out", help="out put form")
    (opts, args) = parser.parse_args()
    if opts.__bucket and opts.endpoint and opts.id and opts.key and opts.out:
        get_form(opts.__bucket, opts.endpoint, opts.id, opts.key, opts.out)
    else:
        print(
            "python %s --__bucket=your-__bucket --endpoint=oss-cn-hangzhou.aliyuncs.com --id=your-access-key-id --key=your-access-key-secret --out=out-put-form-name" % __file__)
'''
用法：

python post_object.py 
--__bucket=您的Bucket 
--endpoint=Bucket对应的OSS域名 
--id=您的AccessKeyId 
--key=您的AccessKeySecret 
--out=输出的文件名


示例：
python post_object.py --__bucket=oss-sample --endpoint=oss-cn-hangzhou.aliyuncs.com --id=tphpxp --key=ZQNJzf4QJRkrH4 --out=post.html
'''
