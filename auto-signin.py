import requests
import ddddocr
import os
from io import BytesIO
from typing import Optional, Tuple
import time

# 用户登录信息
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

# API 端点
BASE_URL = "https://999865.xyz"
LOGIN_URL = f"{BASE_URL}/api/user/login"
CAPTCHA_URL = f"{BASE_URL}/captcha"
SIGN_URL = f"{BASE_URL}/api/user/sign"

# 最大重试次数
MAX_RETRIES = 5
RETRY_DELAY = 10  # 秒

def login() -> Optional[str]:
    """登录并获取 token"""
    try:
        headers = {"Content-Type": "application/json"}
        payload = {"username": USERNAME, "password": PASSWORD}
        response = requests.post(LOGIN_URL, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if data.get("status") == 1:
            return data.get("data")
        print(f"登录失败: {data.get('message', '未知错误')}")
    except requests.RequestException as e:
        print(f"登录请求异常: {e}")
    return None

def get_captcha_and_cookie() -> Tuple[Optional[bytes], Optional[str]]:
    """获取验证码图片和 vpnpn888 cookie"""
    try:
        response = requests.get(CAPTCHA_URL, timeout=10)
        response.raise_for_status()
        
        cookies = response.headers.get("set-cookie", "")
        vpnpn888 = next((cookie.strip() for cookie in cookies.split(";") if "vpnpn888=" in cookie), None)
        return response.content, vpnpn888
    except requests.RequestException as e:
        print(f"获取验证码失败: {e}")
    return None, None

def recognize_captcha(image_content: bytes) -> Optional[str]:
    """使用 ddddocr 识别验证码"""
    try:
        ocr = ddddocr.DdddOcr(show_ad=False)
        return ocr.classification(image_content)
    except Exception as e:
        print(f"验证码识别失败: {e}")
    return None

def sign_in(token: str, captcha_code: str, vpnpn888: str) -> bool:
    """执行签到，返回是否成功"""
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Cookie": f"token={token}; {vpnpn888}"
        }
        sign_url = f"{SIGN_URL}?v={captcha_code}"
        response = requests.get(sign_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if data.get("status") == 1:
            print(f"签到成功: {data.get('message')}")
            return True
        elif "已签到" in data.get("message", ""):
            print(f"今日已签到: {data.get('message')}")
            return True
        else:
            print(f"签到失败: {data.get('message')}")
            return False
    except requests.RequestException as e:
        print(f"签到请求失败: {e}")
        return False

def main():
    if not USERNAME or not PASSWORD:
        print("错误: 未设置用户名或密码环境变量")
        return
    
    # 1. 登录
    token = login()
    if not token:
        return
    
    # 2. 尝试签到（最多重试 MAX_RETRIES 次）
    for attempt in range(MAX_RETRIES):
        # 获取验证码图片和 cookie
        captcha_image, vpnpn888 = get_captcha_and_cookie()
        if not captcha_image or not vpnpn888:
            print(f"尝试 {attempt + 1}/{MAX_RETRIES} 失败: 无法获取验证码")
            time.sleep(RETRY_DELAY)
            continue
        
        # 识别验证码
        captcha_code = recognize_captcha(captcha_image)
        if not captcha_code:
            print(f"尝试 {attempt + 1}/{MAX_RETRIES} 失败: 验证码识别失败")
            time.sleep(RETRY_DELAY)
            continue
        
        # 执行签到
        if sign_in(token, captcha_code, vpnpn888):
            return
        
        print(f"尝试 {attempt + 1}/{MAX_RETRIES} 失败，等待 {RETRY_DELAY} 秒后重试")
        time.sleep(RETRY_DELAY)
    
    print("达到最大重试次数，签到失败")

if __name__ == "__main__":
    main()