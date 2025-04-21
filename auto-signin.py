import requests
import ddddocr
import json
from io import BytesIO
import os

# 用户登录信息
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

# API 端点
LOGIN_URL = "https://999865.xyz/api/user/login"
CAPTCHA_URL = "https://999865.xyz/captcha"
SIGN_URL = "https://999865.xyz/api/user/sign"

def login():
    """登录并获取 token"""
    headers = {"Content-Type": "application/json"}
    payload = {"username": USERNAME, "password": PASSWORD}
    response = requests.post(LOGIN_URL, json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("status") == 1:
            return data.get("data")  # 返回 token
    print("登录失败:", response.text)
    return None

def get_captcha_and_cookie():
    """获取验证码图片和 vpnpn888 cookie"""
    response = requests.get(CAPTCHA_URL)
    
    if response.status_code == 200:
        # 从 headers 中获取 set-cookie
        cookies = response.headers.get("set-cookie")
        vpnpn888 = None
        if cookies:
            for cookie in cookies.split(";"):
                if "vpnpn888=" in cookie:
                    vpnpn888 = cookie.strip()
                    break
        return response.content, vpnpn888
    print("获取验证码失败:", response.text)
    return None, None

def recognize_captcha(image_content):
    """使用 ddddocr 识别验证码"""
    ocr = ddddocr.DdddOcr()
    try:
        captcha_code = ocr.classification(image_content)
        return captcha_code
    except Exception as e:
        print("验证码识别失败:", e)
        return None

def sign_in(token, captcha_code, vpnpn888):
    """执行签到"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Cookie": f"token={token}; {vpnpn888}"
    }
    sign_url = f"{SIGN_URL}?v={captcha_code}"
    response = requests.get(sign_url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("status") == 1:
            print("签到成功:", data.get("message"))
        else:
            print("签到失败:", data.get("message"))
    else:
        print("签到请求失败:", response.text)

def main():
    # 1. 登录
    token = login()
    if not token:
        return
    
    # 2. 获取验证码图片和 cookie
    captcha_image, vpnpn888 = get_captcha_and_cookie()
    if not captcha_image or not vpnpn888:
        return
    
    # 3. 识别验证码
    captcha_code = recognize_captcha(captcha_image)
    if not captcha_code:
        return
    
    # 4. 签到
    sign_in(token, captcha_code, vpnpn888)

if __name__ == "__main__":
    main()