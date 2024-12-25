"""
实现用户后端接口
提供了 HTTP 路由，接收客户端请求并调用 user 类的方法。
定义了一个 Flask 蓝图
用于用户相关的功能，具体功能包括登录，登出，注册，注销，修改秘密，书籍查询
与原来的bookstore相比，用户部分增加查询书籍功能
接口代码不用变，给新功能增加接口即可
"""

from flask import Blueprint
from flask import request
from flask import jsonify
from be.model import user

bp_auth = Blueprint("auth", __name__, url_prefix="/auth")


@bp_auth.route("/login", methods=["POST"])
def login():
    user_id = request.json.get("user_id", "")
    password = request.json.get("password", "")
    terminal = request.json.get("terminal", "")
    u = user.User()
    code, message, token = u.login(
        user_id=user_id, password=password, terminal=terminal
    )
    return jsonify({"message": message, "token": token}), code


@bp_auth.route("/logout", methods=["POST"])
def logout():
    user_id: str = request.json.get("user_id")
    token: str = request.headers.get("token")
    u = user.User()
    code, message = u.logout(user_id=user_id, token=token)
    return jsonify({"message": message}), code


@bp_auth.route("/register", methods=["POST"])
def register():
    user_id = request.json.get("user_id", "")
    password = request.json.get("password", "")
    u = user.User()
    code, message = u.register(user_id=user_id, password=password)
    return jsonify({"message": message}), code


@bp_auth.route("/unregister", methods=["POST"])
def unregister():
    user_id = request.json.get("user_id", "")
    password = request.json.get("password", "")
    u = user.User()
    code, message = u.unregister(user_id=user_id, password=password)
    return jsonify({"message": message}), code


@bp_auth.route("/password", methods=["POST"])
def change_password():
    user_id = request.json.get("user_id", "")
    old_password = request.json.get("oldPassword", "")
    new_password = request.json.get("newPassword", "")
    u = user.User()
    code, message = u.change_password(
        user_id=user_id, old_password=old_password, new_password=new_password
    )
    return jsonify({"message": message}), code


# 仿造上面的写法增加新路由
# 新增书籍搜索功能：搜索范围包括，题目，标签，目录，全站搜索或是当前店铺搜索
# 虽然项目要求搜索范围还要包括内容，但是books文档中与内容无关，因此忽略这部分
# 调用user类中的search_book函数
@bp_auth.route("/search_book", methods=["POST"])
def search_book():
    title = request.json.get("title", "")
    content = request.json.get("content", "")
    tag = request.json.get("tag", "")
    store_id = request.json.get("store_id", "")
    u = user.User()
    code, result = u.search_book(title=title, content=content, tag=tag, store_id=store_id)
    return jsonify({"message": result}), code
