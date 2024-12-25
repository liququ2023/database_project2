"""
这部分实现买家的请求
买家增加获取历史订单，取消订单以及确认收货功能
"""

import requests
import simplejson
from urllib.parse import urljoin
from fe.access.auth import Auth

'''
定义了一个 Buyer 类，负责处理买家操作及与远程 API 的交互。
'''
class Buyer:
    def __init__(self, url_prefix, user_id, password):
        """
        url_prefix:基础 URL，用于构建请求的完整 URL
        user_id:买家的用户 ID
        password:买家的密码
        self.token: 初始化时为空，会通过登录获取
        self.terminal: 终端信息，用于标识请求来源。
        """
        self.url_prefix = urljoin(url_prefix, "buyer/")
        self.user_id = user_id
        self.password = password
        self.token = ""
        self.terminal = "my terminal"
        """
        这部分实现登录操作
        创建 Auth 对象以处理身份验证
        调用 login 方法进行登录，并获取状态码和令牌
        使用 assert 确保登录成功
        """
        self.auth = Auth(url_prefix)
        code, self.token = self.auth.login(self.user_id, self.password, self.terminal)
        assert code == 200

    def new_order(self, store_id: str, book_id_and_count: [(str, int)]) -> (int, str):
        """
        此方法用于创建新订单
        :param store_id: 店铺ID
        :param book_id_and_count:包含书籍 ID 和数量的元组列表
        :return:状态码和订单号
        """
        books = []
        for id_count_pair in book_id_and_count:
            books.append({"id": id_count_pair[0], "count": id_count_pair[1]})
        json = {"user_id": self.user_id, "store_id": store_id, "books": books}
        # print(simplejson.dumps(json))
        url = urljoin(self.url_prefix, "new_order")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        response_json = r.json()
        return r.status_code, response_json.get("order_id")

    def payment(self, order_id: str):
        """
        支付订单
        :param order_id:订单号
        :return:状态码
        """
        json = {
            "user_id": self.user_id,
            "password": self.password,
            "order_id": order_id,
        }
        url = urljoin(self.url_prefix, "payment")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code

    def add_funds(self, add_value: str) -> int:
        """
        账户充值
        :param add_value:充值金额
        :return:状态码
        """
        json = {
            "user_id": self.user_id,
            "password": self.password,
            "add_value": add_value,
        }
        url = urljoin(self.url_prefix, "add_funds")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code

    def get_history_order(self) -> int:
        """
        获取历史订单
        :return:状态码
        """
        json = {
            "user_id": self.user_id,
        }
        url = urljoin(self.url_prefix, "get_history_order")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code

    def cancel_order(self, order_id: str) -> int:
        """
        取消订单
        :param order_id:订单号
        :return:状态码
        """
        json = {
            "user_id": self.user_id,
            "order_id": order_id,
        }
        url = urljoin(self.url_prefix, "cancel_order")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code

    def receive_order(self, order_id: str) -> int:
        """
        确认收货
        :param order_id:订单号
        :return:状态码
        """
        json = {
            "user_id": self.user_id,
            "order_id": order_id,
        }
        url = urljoin(self.url_prefix, "receive_order")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code
