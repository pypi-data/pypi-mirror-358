"""
# File       : tools.py
# Time       ：2024/9/3 上午4:29
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from pathlib import Path
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization


def crt证书_解析成_pem公钥(cert_file_path: Path):
    # 读取证书文件
    with open(cert_file_path, "rb") as cert_file:
        cert_data = cert_file.read()

    # 加载证书
    cert = x509.load_pem_x509_certificate(cert_data, default_backend())

    # 提取公钥
    public_key = cert.public_key()

    # 将公钥转换为PEM格式字符串
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8').strip()

    return public_key_pem
