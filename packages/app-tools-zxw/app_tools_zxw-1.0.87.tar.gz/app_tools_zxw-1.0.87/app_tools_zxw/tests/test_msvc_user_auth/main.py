"""
# File       : main.py
# Time       ：2024/8/27 下午5:42
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app_tools_zxw.msvc_user_auth.apis import router

app = FastAPI(title="app-tools-zxw 接口-用户微服务")
app.include_router(router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
