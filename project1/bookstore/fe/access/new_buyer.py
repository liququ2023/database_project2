"""
定义了一个 register_new_buyer 函数，用于注册新的买家并返回一个 Buyer 实例
接收 user_id 和 password 作为参数
此文件不需要改动，没有新功能在这里加入
"""

from fe import conf
from fe.access import buyer, auth

def register_new_buyer(user_id, password) -> buyer.Buyer:
    a = auth.Auth(conf.URL)  # 创建一个 Auth 对象 a，用于处理身份验证相关的操作
    code = a.register(user_id, password)  # 调用 Auth 对象的 register 方法，尝试注册用户
    assert code == 200  # 检查 code 是否等于200
    s = buyer.Buyer(conf.URL, user_id, password)  # 创建一个新的 Buyer 对象 s，并将 conf.URL、user_id 和 password 作为参数传递给 Buyer 的构造函数
    return s  # 返回新创建的 Buyer 对象 s
