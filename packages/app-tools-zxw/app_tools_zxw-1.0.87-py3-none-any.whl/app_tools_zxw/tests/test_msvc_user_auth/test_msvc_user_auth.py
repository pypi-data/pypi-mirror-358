"""
# File       : test_msvc_user_auth.py
# Time       ：2024/8/27 下午5:40
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
        ！！！！！！！！必须使用Python3.12环境，app-tools-zxw默认环境是Python3.9
"""
import pytest
from httpx import AsyncClient
from app_tools_zxw.tests.test_msvc_user_auth.main import app  # 替换为你 FastAPI 应用的实际导入路径
from app_tools_zxw.msvc_user_auth.schemas import *

# base_url = "http://localhost:8000"
base_url = "http://test"


@pytest.fixture
async def login_user():
    async def _login_user(username: str = "string4", password: str = "string"):
        # print("正在执行登录，用户名：", username, "密码：", password)
        async with AsyncClient(app=app, base_url=base_url) as ac:
            response = await ac.post("/user_center/account/login", json={
                "username": username,
                "password": password
            })

        if response.status_code != 200:
            # print(response.json())
            return None, None, response
        else:
            access_token = response.json()["access_token"]
            refresh_token = response.json()["refresh_token"]
            user_info = response.json()["user_info"]

            return access_token, refresh_token, user_info

    return _login_user


# 预置已注册的账号（假设这些操作是提前在数据库中完成的）
# 	scope="module"：该 fixture 的作用域设置为 module，表示它在每个测试模块中仅执行一次。
#  	                这样可以确保注册过程不会在每个测试用例中重复执行。
# 	autouse=True：确保该 fixture 自动在所有测试用例之前执行，而不需要显式调用。
@pytest.fixture(scope="module", autouse=True)
async def pre_register_existing_users():
    async with AsyncClient(app=app, base_url=base_url) as ac:
        for i in range(50):
            await ac.post("/user_center/account/register", json={
                "username": f"existing_user_{i}",
                "password": "password",
                "role_name": "test_role",
                "app_name": "test_app"
            })
            await ac.post("/user_center/account/register", json={
                "username": f"existing_user_{i}_nopass",
                "password": "password",
                "role_name": "test_role",
                "app_name": "test_app"
            })


@pytest.mark.asyncio
async def test_register_user():
    test_cases = []

    # 生成测试用例
    for i in range(50):
        # 未注册账号
        test_cases.append({"username": f"new_user_{i}", "password": "password", "expected_status": 200})
        # 已注册账号
        test_cases.append({"username": f"existing_user_{i}", "password": "password", "expected_status": 400})
        # 未注册账号，密码为空
        test_cases.append({"username": f"new_user_{i}_nopass", "password": "", "expected_status": 422})
        # 已注册账号，密码为空
        test_cases.append({"username": f"existing_user_{i}_nopass", "password": "", "expected_status": 400})

    async with AsyncClient(app=app, base_url=base_url) as ac:
        for case in test_cases:
            response = await ac.post("/user_center/account/register", json={
                "username": case["username"],
                "password": case["password"],
                "role_name": "test_role",
                "app_name": "test_app"
            })

            # assert response.status_code == case["expected_status"], f"Failed for {case}"

            if case["expected_status"] == 200:
                print("注册成功,response:", response.json())
                assert "access_token" in response.json()
                assert "refresh_token" in response.json()
                assert "user_info" in response.json()
            elif case["expected_status"] == 400:
                # 检查已注册账号的错误信息
                print(response.json())
                # assert "error" in response.json()
            elif case["expected_status"] == 422:
                # 检查密码为空的错误信息
                print(response.json())
                assert "detail" in response.json()


@pytest.mark.asyncio
async def test_login_user(login_user):
    status_list = []
    success_responses = []
    failure_responses = []

    for i in range(100):
        access_token, refresh_token, user_info = await login_user(f"string{i}", "string")

        if access_token is None:
            # 登录失败
            status_list.append(False)
            failure_responses.append(user_info)
        else:
            # 登录成功
            status_list.append(True)
            success_responses.append(user_info)

    # 检查登录结果
    assert len(success_responses) > 0, "所有登录尝试都失败了"
    assert len(failure_responses) > 0, "所有登录尝试都成功了"

    # 打印或记录详细信息（如果需要）
    print(f"成功登录的账号数量: {len(success_responses)}")
    print(f"失败登录的账号数量: {len(failure_responses)}")

    # 如果需要进一步处理失败的响应
    for response in failure_responses:
        print(f"登录失败的用户信息: {response.json()}")


@pytest.mark.asyncio
async def test_get_wechat_qrcode():
    async with AsyncClient(app=app, base_url=base_url) as ac:
        response = await ac.post("/user_center/wechat/get-login-qrcode", json={
            "WECHAT_REDIRECT_URI": "https://example.com/redirect"
        })
    assert response.status_code == 200
    assert "qr_code_url" in response.json()


@pytest.mark.asyncio
async def test_refresh_token(login_user):
    access_token, refresh_token, user_info = await login_user()
    async with AsyncClient(app=app, base_url=base_url) as ac:
        ac.headers["Authorization"] = f"Bearer {access_token}"

        response = await ac.post("/user_center/token/refresh", json={
            "refresh_token": refresh_token
        })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()


@pytest.mark.asyncio
async def test_get_current_user(login_user):
    access_token, _, _ = await login_user()
    async with AsyncClient(app=app, base_url=base_url) as ac:
        ac.headers["Authorization"] = f"Bearer {access_token}"

        response = await ac.post("/user_center/get-current-user")
    assert response.status_code == 200
    assert "username" in response.json()
    assert "roles" in response.json()
