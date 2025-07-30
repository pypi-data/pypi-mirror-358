"""
# File       : 初始化logger.py
# Time       ：2024/8/28 下午1:13
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：在 FastAPI 中初始化 logger，在其他的路由文件中引用 logger
            例如：在main.py中，引用logger ,用作初始化
                            from app_tools_zxw.FUNCs_支付相关.初始化logger import logger
                在apis/支付_支付宝_二维码/api_支付_支付宝_二维码.py中，引用logger：
                            from app_tools_zxw.FUNCs_支付相关.初始化logger import logger
"""
import logging
from logging.handlers import RotatingFileHandler
import os
from fastapi.logger import logger as fastapi_logger


def setup_logger(
        log_name: str, log_level=logging.INFO):
    # 创建 logs 目录（如果不存在）
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # 获取指定名称的logger
    logger = logging.getLogger(log_name)

    # 如果logger已经有处理器，说明已经初始化过，直接返回
    if logger.handlers:
        return logger

    # 设置logger级别
    logger.setLevel(log_level)

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)

    # 创建文件处理器（10MB）
    file_handler = RotatingFileHandler(
        f"logs/{log_name}.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)

    # 创建格式化器
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # 添加处理器到logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # 配置 FastAPI 的日志记录器
    fastapi_logger.handlers = logger.handlers

    return logger


# 创建并配置 logger
logger = setup_logger("app")
logger.info("测试")
