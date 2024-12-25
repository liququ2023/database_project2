"""
定义了一个 register_new_seller 函数，用于注册新的买家并返回一个 seller 实例
接收 user_id 和 password 作为参数
此文件不需要改动，没有新功能在这里加入
"""

from fe import conf
from fe.access import seller, auth

def register_new_seller(user_id, password) -> seller.Seller:  # 返回一个seller对象
    a = auth.Auth(conf.URL)  # 创建一个 Auth 对象 a，用于处理与身份验证相关的操作
    code = a.register(user_id, password)  # 调用 Auth 对象的 register 方法，尝试注册卖家
    assert code == 200
    s = seller.Seller(conf.URL, user_id, password)  # 创建一个新的 Seller ，并将 conf.URL、user_id 和 password 作为参数传递给 Seller 的构造函数
    return s  # 返回新创建的 Seller 对象 s
