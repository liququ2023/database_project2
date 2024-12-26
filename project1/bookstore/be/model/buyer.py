import threading
import psycopg2
import uuid
import json
from be.model import db_conn
from be.model import error
from datetime import datetime


class Buyer(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def new_order(self, user_id: str, store_id: str, id_and_count: [(str, int)]) -> (int, str, str):
        order_id = ""
        cursor = None
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id,)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id,)

            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))

            with self.conn:
                cursor = self.conn.cursor()

                for book_id, count in id_and_count:
                    cursor.execute(
                        "SELECT book_id, stock_level, book_info FROM store "
                        "WHERE store_id = %s AND book_id = %s;",
                        (store_id, book_id)
                    )
                    row = cursor.fetchone()
                    if row is None:
                        return error.error_non_exist_book_id(book_id) + (order_id,)

                    stock_level = row[1]
                    book_info = row[2]
                    book_info_json = json.loads(book_info)
                    price = book_info_json.get("price")

                    if stock_level < count:
                        return error.error_stock_level_low(book_id) + (order_id,)

                    cursor.execute(
                        "UPDATE store SET stock_level = stock_level - %s "
                        "WHERE store_id = %s AND book_id = %s AND stock_level >= %s;",
                        (count, store_id, book_id, count)
                    )
                    if cursor.rowcount == 0:
                        return error.error_stock_level_low(book_id) + (order_id,)

                    cursor.execute(
                        "INSERT INTO new_order_detail(order_id, book_id, count, price) "
                        "VALUES (%s, %s, %s, %s);",
                        (uid, book_id, count, price)
                    )

                # 创建订单时，不再在 new_order 中设置状态，而是在历史订单表中设置
                cursor.execute(
                    "INSERT INTO new_order(order_id, store_id, user_id) "
                    "VALUES (%s, %s, %s);",
                    (uid, store_id, user_id)
                )

                # 创建历史订单时，状态设置为 'pending'
                cursor.execute(
                    "INSERT INTO history_order(order_id, store_id, user_id, order_status) "
                    "VALUES (%s, %s, %s, %s);",
                    (uid, store_id, user_id, 'pending')
                )

                self.conn.commit()
                order_id = uid

            # 设置一个定时器，在30秒后调用 cancel_order 方法取消订单
            timer = threading.Timer(30.0, self.cancel_order, args=[user_id, order_id])
            timer.start()  # 延迟队列

        except psycopg2.Error as e:
            self.conn.rollback()  # 发生错误时回滚事务
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            self.conn.rollback()  # 发生错误时回滚事务
            return 530, "{}".format(str(e)), ""

        return 200, "ok", order_id

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        cursor = None
        try:
            cursor = self.conn.cursor()

            # 查询订单信息
            cursor.execute(
                "SELECT order_id, user_id, store_id, order_status FROM history_order WHERE order_id = %s",
                (order_id,)
            )
            row = cursor.fetchone()
            if row is None:
                return error.error_invalid_order_id(order_id)

            order_id_db = row[0]
            buyer_id = row[1]
            store_id = row[2]
            order_status = row[3]

            if buyer_id != user_id:
                return error.error_authorization_fail()

            if order_status != 'pending':  # 只允许支付处于 'pending' 状态的订单
                return error.error_invalid_order_status(order_id)

            cursor.execute(
                "SELECT balance, password FROM \"user\" WHERE user_id = %s;",
                (buyer_id,)
            )
            row = cursor.fetchone()
            if row is None:
                return error.error_non_exist_user_id(buyer_id)
            balance = row[0]
            if password != row[1]:
                return error.error_authorization_fail()

            cursor.execute(
                "SELECT store_id, user_id FROM user_store WHERE store_id = %s;",
                (store_id,)
            )
            row = cursor.fetchone()
            if row is None:
                return error.error_non_exist_store_id(store_id)

            seller_id = row[1]

            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            cursor.execute(
                "SELECT book_id, count, price FROM new_order_detail WHERE order_id = %s;",
                (order_id,)
            )
            total_price = 0
            for row in cursor:
                count = row[1]
                price = row[2]
                total_price += price * count

            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)

            with self.conn:
                cursor.execute(
                    "UPDATE \"user\" SET balance = balance - %s WHERE user_id = %s AND balance >= %s",
                    (total_price, buyer_id, total_price)
                )
                if cursor.rowcount == 0:
                    return error.error_not_sufficient_funds(order_id)

                cursor.execute(
                    "UPDATE \"user\" SET balance = balance + %s WHERE user_id = %s",
                    (total_price, seller_id)
                )

                if cursor.rowcount == 0:
                    return error.error_non_exist_user_id(seller_id)

                # 支付成功后，更新历史订单表中的订单状态为 'paid'
                cursor.execute(
                    "UPDATE history_order SET order_status = %s WHERE order_id = %s",
                    ('paid', order_id)
                )

                self.conn.commit()

        except psycopg2.Error as e:
            self.conn.rollback()  # 发生错误时回滚事务
            return 528, "{}".format(str(e))

        except BaseException as e:
            self.conn.rollback()  # 发生错误时回滚事务
            return 530, "{}".format(str(e))

        return 200, "ok"

    def add_funds(self, user_id, password, add_value) -> (int, str):
        cursor = None
        try:
            cursor = self.conn.cursor()

            # 查找用户的密码
            cursor.execute(
                "SELECT password FROM \"user\" WHERE user_id = %s",
                (user_id,)
            )
            row = cursor.fetchone()
            if row is None:
                return error.error_authorization_fail()

            # 比对密码
            if row[0].strip() != password.strip():
                return error.error_authorization_fail()

            with self.conn:
                # 更新用户余额
                cursor.execute(
                    "UPDATE \"user\" SET balance = balance + %s WHERE user_id = %s",
                    (add_value, user_id)
                )

                if cursor.rowcount <= 0:  # 这里使用 <= 0 来捕捉更新失败的情况
                    return error.error_non_exist_user_id(user_id)

                self.conn.commit()

        except psycopg2.Error as e:
            self.conn.rollback()  # 发生错误时回滚事务
            return 528, "{}".format(str(e))

        except BaseException as e:
            self.conn.rollback()  # 发生错误时回滚事务
            return 530, "{}".format(str(e))

        return 200, "ok"

    def get_history_order(self, user_id: str) -> (int, str, [dict]):
        cursor = None
        try:
            cursor = self.conn.cursor()

            # 获取历史订单
            cursor.execute(
                "SELECT order_id, order_status FROM history_order WHERE user_id = %s;",
                (user_id,)
            )
            orders = cursor.fetchall()

            if not orders:
                return error.error_non_exist_user_id(user_id) + ([],)

            order_list = []
            for order in orders:
                order_id = order[0]
                order_status = order[1]

                # 获取该订单的详情
                cursor.execute(
                    "SELECT book_id, count, price FROM history_order_detail WHERE order_id = %s;",
                    (order_id,)
                )
                order_details = cursor.fetchall()

                order_detail_list = []
                for detail in order_details:
                    book_id = detail[0]
                    count = detail[1]
                    price = detail[2]
                    order_detail = {
                        "book_id": book_id,
                        "count": count,
                        "price": price
                    }
                    order_detail_list.append(order_detail)

                # 构建订单信息
                order_info = {
                    "order_id": order_id,
                    "order_status": order_status,
                    "order_detail": order_detail_list
                }
                order_list.append(order_info)

            return 200, "ok", order_list

        except psycopg2.Error as e:
            self.conn.rollback()  # 发生错误时回滚事务
            return 528, f"Database error: {str(e)}", []

        except Exception as e:
            self.conn.rollback()  # 发生错误时回滚事务
            return 530, f"Unexpected error: {str(e)}", []

        finally:
            if cursor:
                cursor.close()

    def cancel_order(self, user_id: str, order_id: str) -> (int, str):
        cursor = None
        try:
            cursor = self.conn.cursor()

            # 开始取消订单的逻辑
            cursor.execute(
                "SELECT order_id, user_id, order_status FROM history_order WHERE order_id = %s;",
                (order_id,)
            )
            row = cursor.fetchone()
            if row is None:
                return error.error_invalid_order_id(order_id)

            order_id_db = row[0]
            order_user_id = row[1]
            order_status = row[2]
            if order_user_id != user_id:
                return error.error_authorization_fail()

            if order_status in ['paid', 'cancelled']:  # 只有 'pending' 状态的订单可以取消
                return error.error_invalid_order_status(order_id)

            with self.conn:
                cursor.execute(
                    "UPDATE history_order SET order_status = %s WHERE order_id = %s;",
                    ('cancelled', order_id)
                )

                # 删除订单
                cursor.execute(
                    "DELETE FROM new_order WHERE order_id = %s;",
                    (order_id,)
                )
                cursor.execute(
                    "DELETE FROM new_order_detail WHERE order_id = %s;",
                    (order_id,)
                )

                self.conn.commit()

        except psycopg2.Error as e:
            self.conn.rollback()  # 发生错误时回滚事务
            return 528, f"Error: {str(e)}"

        except BaseException as e:
            self.conn.rollback()  # 发生错误时回滚事务
            return 530, f"Unexpected error: {str(e)}"

        return 200, "ok"

    def receive_order(self, user_id: str, order_id: str) -> (int, str):
        try:
            # 1. 查询订单信息
            with self.conn.cursor() as cursor:
                cursor.execute("SELECT order_id, user_id, order_status FROM history_order WHERE order_id = %s",
                               (order_id,))
                order = cursor.fetchone()

                if not order:
                    return self.error_invalid_order_id(order_id)

                # 2. 检查用户身份是否匹配
                order_id_db, buyer_id, status = order
                if buyer_id != user_id:
                    return self.error_authorization_fail()

                # 3. 检查订单状态
                if status != "sent":
                    return self.error_order_not_sent(order_id)

                # 4. 更新订单状态为 'received'
                cursor.execute(
                    "UPDATE history_order SET order_status = %s WHERE order_id = %s AND user_id = %s",
                    ("received", order_id, user_id)
                )

                if cursor.rowcount == 0:
                    return self.error_order_already_received(order_id)

            # 事务提交
            self.conn.commit()

        except psycopg2.Error as e:
            # 数据库错误处理
            self.conn.rollback()  # 如果发生异常，则回滚事务
            return 528, f"Database error: {str(e)}"
        except Exception as e:
            # 其他错误处理
            self.conn.rollback()  # 如果发生异常，则回滚事务
            return 530, f"Unexpected error: {str(e)}"

        return 200, "Order received successfully"