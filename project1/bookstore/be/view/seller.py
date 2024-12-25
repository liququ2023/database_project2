"""
实现卖家的后端接口
提供了 HTTP 路由，接收客户端请求并调用 Seller 类的方法。
每个接口函数在接收到请求后，解析参数，然后调用相应的 Seller 方法。
定义了一个 Flask 蓝图
用于处理与卖家相关的功能，具体功能包括创建商店、添加书籍以及增加库存
与原来的bookstore相比，卖家部分增加发货功能
接口代码不用变，给新功能增加接口即可
"""

from flask import Blueprint
from flask import request
from flask import jsonify
from be.model import seller
import json

# 创建一个名为 seller 的蓝图，所有与卖家相关的路由都将以 /seller 开头
bp_seller = Blueprint("seller", __name__, url_prefix="/seller")


# 定义一系列路由处理函数，收到对应url的请求时，将调用对应函数

# 卖家新建店铺
@bp_seller.route("/create_store", methods=["POST"])
def seller_create_store():
    """
    从请求中获取 user_id 和 store_id，创建一个 Seller 实例，并调用 create_store 方法。
    :return: 以 JSON 格式返回消息和状态码
    """
    user_id: str = request.json.get("user_id")
    store_id: str = request.json.get("store_id")
    s = seller.Seller()
    code, message = s.create_store(user_id, store_id)  # 调用对应的函数
    return jsonify({"message": message}), code


# 在店铺中增加书籍
@bp_seller.route("/add_book", methods=["POST"])
def seller_add_book():
    # 从请求体中获得信息
    user_id: str = request.json.get("user_id")
    store_id: str = request.json.get("store_id")
    book_info: str = request.json.get("book_info")
    stock_level: str = request.json.get("stock_level", 0)

    s = seller.Seller()
    # 调用seller类的add_book方法
    code, message = s.add_book(
        user_id, store_id, book_info.get("id"), json.dumps(book_info), stock_level
        # json.dumps() 是 Python 标准库 json 中的一个函数，用于将 Python 对象转换为 JSON 格式的字符串
    )

    return jsonify({"message": message}), code


# 在店铺增加库存
@bp_seller.route("/add_stock_level", methods=["POST"])
def add_stock_level():
    user_id: str = request.json.get("user_id")
    store_id: str = request.json.get("store_id")
    book_id: str = request.json.get("book_id")
    add_num: str = request.json.get("add_stock_level", 0)

    s = seller.Seller()
    code, message = s.add_stock_level(user_id, store_id, book_id, add_num)

    return jsonify({"message": message}), code


# 仿照上面的增加新的后端接口
# 店铺发货
@bp_seller.route("/send_order", methods=["POST"])
def send_order():
    user_id: str = request.json.get("user_id")
    store_id: str = request.json.get("store_id")
    order_id: str = request.json.get("order_id")

    s = seller.Seller()
    code, message = s.send_order(user_id, store_id, order_id)

    return jsonify({"message": message}), code
