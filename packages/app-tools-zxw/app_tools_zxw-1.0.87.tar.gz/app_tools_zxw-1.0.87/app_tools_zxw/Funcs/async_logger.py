"""
# File       : async_logger.py
# Time       ：2025/2/10 08:43
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
import os
import logging
from logging.handlers import RotatingFileHandler

import aiofiles
import asyncio
from logging.handlers import QueueHandler, QueueListener
from queue import Queue


class __AsyncRotatingFileHandler(RotatingFileHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loop = None

    async def async_emit(self, record):
        try:
            msg = self.format(record)
            async with aiofiles.open(self.baseFilename, 'a', encoding=self.encoding) as f:
                await f.write(msg + self.terminator)
        except Exception:
            self.handleError(record)

    def emit(self, record):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # 如果没有运行中的事件循环，则同步写入
            msg = self.format(record)
            with open(self.baseFilename, 'a', encoding=self.encoding) as f:
                f.write(msg + self.terminator)
        else:
            loop.create_task(self.async_emit(record))


def setup_logger(
        log_name: str,
        log_level=logging.INFO,
        to_console=True,
        to_file=True
):
    # 创建 logs 目录（如果不存在）
    if to_file and not os.path.exists("logs"):
        os.makedirs("logs")

    # 创建队列
    log_queue = Queue()

    logger = logging.getLogger(log_name)
    if logger.handlers:
        return logger

    logger.setLevel(log_level)

    handlers = []

    # 根据参数决定是否添加文件处理器
    if to_file:
        file_handler = __AsyncRotatingFileHandler(
            f"logs/{log_name}.log",
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        handlers.append(file_handler)

    # 根据参数决定是否添加控制台处理器
    if to_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        handlers.append(console_handler)

    # 只有在有处理器的情况下才创建队列处理器和监听器
    if handlers:
        # 创建队列处理器
        queue_handler = QueueHandler(log_queue)
        logger.addHandler(queue_handler)

        # 创建队列监听器
        listener = QueueListener(
            log_queue,
            *handlers,
            respect_handler_level=True
        )
        listener.start()

    return logger


if __name__ == "__main__":
    # 如果需要测试，建议添加以下代码：
    async def tlogger():
        ilogger = setup_logger("info", to_file=True, to_console=False)
        ilogger.info("测试")
        # 等待一小段时间确保日志写入完成
        await asyncio.sleep(0.1)


    asyncio.run(tlogger())
