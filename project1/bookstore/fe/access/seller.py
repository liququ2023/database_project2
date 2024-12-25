"""
此文件是卖家部分请求的实现
增加发货功能
"""
import requests
from urllib.parse import urljoin
from fe.access import book
from fe.access.auth import Auth


'''
定义了一个seller类
'''
class Seller:
    def __init__(self, url_prefix, seller_id: str, password: str):
        """
        url_prefix:基础 URL，用于构建请求的完整 URL
        user_id:卖家的用户 ID
        password:卖家的密码
        self.token: 初始化时为空，会通过登录获取
        self.terminal: 终端信息，用于标识请求来源。
        """
        self.url_prefix = urljoin(url_prefix, "seller/")
        self.seller_id = seller_id
        self.password = password
        self.terminal = "my terminal"
        """
        这部分实现登录操作
        创建 Auth 对象以处理身份验证
        调用 login 方法进行登录，并获取状态码和令牌
        使用 assert 确保登录成功
        """
        self.auth = Auth(url_prefix)
        code, self.token = self.auth.login(self.seller_id, self.password, self.terminal)
        assert code == 200

    def create_store(self, store_id):
        json = {
            "user_id": self.seller_id,
            "store_id": store_id,
        }
        # print(simplejson.dumps(json))
        url = urljoin(self.url_prefix, "create_store")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code

    def add_book(self, store_id: str, stock_level: int, book_info: book.Book) -> int:
        json = {
            "user_id": self.seller_id,
            "store_id": store_id,
            "book_info": book_info.__dict__,
            "stock_level": stock_level,
        }
        # print(simplejson.dumps(json))
        url = urljoin(self.url_prefix, "add_book")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code

    def add_stock_level(
            self, seller_id: str, store_id: str, book_id: str, add_stock_num: int
    ) -> int:
        """
        增加库存
        :param seller_id: 卖家ID
        :param store_id: 店铺ID
        :param book_id: 书ID
        :param add_stock_num: 增加库存数
        :return: 状态码
        """
        json = {
            "user_id": seller_id,
            "store_id": store_id,
            "book_id": book_id,
            "add_stock_level": add_stock_num,
        }
        # print(simplejson.dumps(json))
        url = urljoin(self.url_prefix, "add_stock_level")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code

    def send_order(self, store_id: str, order_id: str) -> int:
        """
        用于卖家发货订单
        :param store_id: 店铺ID
        :param order_id: 订单号
        :return: 状态码
        """
        json = {
            "user_id": self.seller_id,
            "store_id": store_id,
            "order_id": order_id,
        }
        url = urljoin(self.url_prefix, "send_order")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code
