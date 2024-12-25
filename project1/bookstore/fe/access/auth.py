"""
名为 Auth 的类，用于处理用户认证和图书搜索的相关操作
增加查找书本功能
"""

import requests
from urllib.parse import urljoin

class Auth:
    def __init__(self, url_prefix):
        """
        初始化方法接受一个 URL 前缀,将URL前缀与 "auth/" 组合，形成完整的认证 URL
        """
        self.url_prefix = urljoin(url_prefix, "auth/")

    def login(self, user_id: str, password: str, terminal: str) -> (int, str):
        """
        实现登录请求
        :param user_id: 接收的用户id
        :param password: 接收的用户密码
        :param terminal: 接收到的终端信息
        发送POST请求
        :return: HTTP状态码，从json数据中提取token，用于后续请求的身份验证
        """
        # json是请求体
        json = {"user_id": user_id, "password": password, "terminal": terminal}
        url = urljoin(self.url_prefix, "login")
        # 发送请求
        r = requests.post(url, json=json)
        return r.status_code, r.json().get("token")

    def register(self, user_id: str, password: str) -> int:
        """
        实现注册请求
        :param user_id: 接受的用户id
        :param password: 接受的用户密码
        发送POST请求
        :return:HTTP状态码
        """
        json = {"user_id": user_id, "password": password}
        url = urljoin(self.url_prefix, "register")
        r = requests.post(url, json=json)
        return r.status_code

    def password(self, user_id: str, old_password: str, new_password: str) -> int:
        """
        修改密码
        :param user_id: 接受的用户id
        :param old_password: 接受的旧用户密码
        :param new_password: 接受的新用户密码
        :return: HTTP状态码
        """
        json = {
            "user_id": user_id,
            "oldPassword": old_password,
            "newPassword": new_password,
        }
        url = urljoin(self.url_prefix, "password")
        r = requests.post(url, json=json)
        return r.status_code

    def logout(self, user_id: str, token: str) -> int:
        """
        用户登出
        :param user_id:接受的用户id
        :param token:用户的身份验证令牌
        :return:HTTP状态码
        """
        json = {"user_id": user_id}
        headers = {"token": token}
        url = urljoin(self.url_prefix, "logout")
        r = requests.post(url, headers=headers, json=json)
        return r.status_code

    def unregister(self, user_id: str, password: str) -> int:
        """
        注销账号
        :param user_id: 用户id
        :param password: 用户密码
        :return: HTTP状态码
        """
        json = {"user_id": user_id, "password": password}
        url = urljoin(self.url_prefix, "unregister")
        r = requests.post(url, json=json)
        return r.status_code

    def search_book(self, title='', content='', tag='', store_id='') -> int:
        """
        搜索书籍
        :param title: 标题
        :param content: 内容
        :param tag: 书籍tag
        :param store_id: 店铺
        :return: HTTP状态码
        """
        json = {"title": title, "content": content, "tag": tag, "store_id": store_id}
        url = urljoin(self.url_prefix, "search_book")
        r = requests.post(url, json=json)
        return r.status_code
