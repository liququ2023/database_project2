import psycopg2
import uuid
import json
import logging
from be.model import db_conn
from be.model import error


class Buyer(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def new_order(
        self, user_id: str, store_id: str, id_and_count: [(str, int)]
    ) -> (int, str, str):
        order_id = ""
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id,)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id,)
            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))

            for book_id, count in id_and_count:
                cursor = self.conn.cursor()
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

            cursor.execute(
                "INSERT INTO new_order(order_id, store_id, user_id) "
                "VALUES (%s, %s, %s);",
                (uid, store_id, user_id)
            )
            self.conn.commit()
            order_id = uid
        except psycopg2.Error as e:
            logging.error("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.error("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""

        return 200, "ok", order_id

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT order_id, user_id, store_id FROM new_order WHERE order_id = %s",
                (order_id,)
            )
            row = cursor.fetchone()
            if row is None:
                return error.error_invalid_order_id(order_id)

            order_id = row[0]
            buyer_id = row[1]
            store_id = row[2]

            if buyer_id != user_id:
                return error.error_authorization_fail()

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
                total_price = total_price + price * count

            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)

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

            cursor.execute(
                "DELETE FROM new_order WHERE order_id = %s",
                (order_id,)
            )
            if cursor.rowcount == 0:
                return error.error_invalid_order_id(order_id)

            cursor.execute(
                "DELETE FROM new_order_detail WHERE order_id = %s",
                (order_id,)
            )
            if cursor.rowcount == 0:
                return error.error_invalid_order_id(order_id)

            self.conn.commit()

        except psycopg2.Error as e:
            return 528, "{}".format(str(e))

        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def add_funds(self, user_id, password, add_value) -> (int, str):
        try:
            cursor = self.conn.cursor()
            logging.info(f"Attempting to add funds for user {user_id} with amount {add_value}")

            # 查找用户的密码
            cursor.execute(
                "SELECT password FROM \"user\" WHERE user_id = %s",
                (user_id,)
            )
            row = cursor.fetchone()
            if row is None:
                logging.error(f"User {user_id} not found in database.")
                return error.error_authorization_fail()

            # 比对密码
            if row[0].strip() != password.strip():
                logging.error(f"Incorrect password for user {user_id}.")
                return error.error_authorization_fail()

            # 更新用户余额
            cursor.execute(
                "UPDATE \"user\" SET balance = balance + %s WHERE user_id = %s",
                (add_value, user_id)
            )

            if cursor.rowcount <= 0:  # 这里使用 <= 0 来捕捉更新失败的情况
                logging.error(f"Failed to update balance for user {user_id}.")
                return error.error_non_exist_user_id(user_id)

            self.conn.commit()
            logging.info(f"Funds added successfully for user {user_id}.")
        except psycopg2.Error as e:
            logging.error(f"Database error while adding funds for user {user_id}: {str(e)}")
            return 528, "{}".format(str(e))
        except BaseException as e:
            logging.error(f"Unexpected error while adding funds for user {user_id}: {str(e)}")
            return 530, "{}".format(str(e))

        return 200, "ok"

    def get_history_order(self, user_id: str) -> (int, str, [dict]):
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

                # 获取历史订单详情
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

                # 拼装订单信息
                order_info = {
                    "order_id": order_id,
                    "order_status": order_status,
                    "order_detail": order_detail_list
                }
                order_list.append(order_info)

            return 200, "ok", order_list

        except psycopg2.Error as e:
            logging.error(f"Database error while getting history orders: {str(e)}")
            return 528, "{}".format(str(e)), []
        except BaseException as e:
            logging.error(f"Unexpected error while getting history orders: {str(e)}")
            return 530, "{}".format(str(e)), []

    def cancel_order(self, user_id: str, order_id: str) -> (int, str):
        try:
            cursor = self.conn.cursor()

            # 检查订单是否存在
            cursor.execute(
                "SELECT order_id, user_id FROM new_order WHERE order_id = %s;",
                (order_id,)
            )
            order = cursor.fetchone()
            if not order:
                return error.error_invalid_order_id(order_id)

            buyer_id = order[1]
            if buyer_id != user_id:
                return error.error_authorization_fail()

            # 删除订单
            cursor.execute(
                "DELETE FROM new_order WHERE order_id = %s;",
                (order_id,)
            )
            if cursor.rowcount == 0:
                return error.error_invalid_order_id(order_id)

            # 删除订单详情
            cursor.execute(
                "DELETE FROM new_order_detail WHERE order_id = %s;",
                (order_id,)
            )
            if cursor.rowcount == 0:
                return error.error_invalid_order_id(order_id)

            # 更新历史订单状态为 cancelled
            cursor.execute(
                "UPDATE history_order SET order_status = 'cancelled' WHERE order_id = %s;",
                (order_id,)
            )
            if cursor.rowcount == 0:
                return error.error_invalid_order_id(order_id)

            self.conn.commit()

        except psycopg2.Error as e:
            logging.error(f"Database error while cancelling order {order_id}: {str(e)}")
            return 528, "{}".format(str(e))
        except BaseException as e:
            logging.error(f"Unexpected error while cancelling order {order_id}: {str(e)}")
            return 530, "{}".format(str(e))

        return 200, "ok"

    def receive_order(self, user_id: str, order_id: str) -> (int, str):
        try:
            cursor = self.conn.cursor()

            # 检查订单是否存在
            cursor.execute(
                "SELECT order_id, user_id, order_status FROM history_order WHERE order_id = %s;",
                (order_id,)
            )
            order = cursor.fetchone()
            if not order:
                return error.error_invalid_order_id(order_id)

            buyer_id = order[1]
            if buyer_id != user_id:
                return error.error_authorization_fail()

            status = order[2]
            if status != "sent":
                return error.error_not_sent(order_id)

            # 更新订单状态为 received
            cursor.execute(
                "UPDATE history_order SET order_status = 'received' WHERE order_id = %s;",
                (order_id,)
            )
            if cursor.rowcount == 0:
                return error.error_invalid_order_id(order_id)

            self.conn.commit()

        except psycopg2.Error as e:
            logging.error(f"Database error while receiving order {order_id}: {str(e)}")
            return 528, "{}".format(str(e))
        except BaseException as e:
            logging.error(f"Unexpected error while receiving order {order_id}: {str(e)}")
            return 530, "{}".format(str(e))

        return 200, "ok"
