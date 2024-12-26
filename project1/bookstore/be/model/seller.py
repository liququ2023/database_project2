import psycopg2
from be.model import error
from be.model import db_conn
import logging

class Seller(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def add_book(
            self,
            user_id: str,
            store_id: str,
            book_id: str,
            book_json_str: str,
            stock_level: int,
    ):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if self.book_id_exist(store_id, book_id):
                return error.error_exist_book_id(book_id)

            # 开启事务
            with self.conn:
                with self.conn.cursor() as cursor:
                    cursor.execute(
                        'INSERT INTO store(store_id, book_id, book_info, stock_level) '
                        'VALUES (%s, %s, %s, %s)',
                        (store_id, book_id, book_json_str, stock_level),
                    )
        except psycopg2.Error as e:
            logging.error(f"Database error while adding book: {str(e)}")
            return 528, "{}".format(str(e))
        except BaseException as e:
            logging.error(f"Unexpected error: {str(e)}")
            return 530, "{}".format(str(e))

        return 200, "ok"

    def add_stock_level(
            self, user_id: str, store_id: str, book_id: str, add_stock_level: int
    ):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if not self.book_id_exist(store_id, book_id):
                return error.error_non_exist_book_id(book_id)

            # 开启事务
            with self.conn:
                with self.conn.cursor() as cursor:
                    cursor.execute(
                        'UPDATE store SET stock_level = stock_level + %s '
                        'WHERE store_id = %s AND book_id = %s',
                        (add_stock_level, store_id, book_id),
                    )
        except psycopg2.Error as e:
            logging.error(f"Database error while updating stock level: {str(e)}")
            return 528, "{}".format(str(e))
        except BaseException as e:
            logging.error(f"Unexpected error: {str(e)}")
            return 530, "{}".format(str(e))

        return 200, "ok"

    def create_store(self, user_id: str, store_id: str) -> (int, str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)

            if self.store_id_exist(store_id):
                return error.error_exist_store_id(store_id)

            # 在事务中进行多个操作
            with self.conn:
                with self.conn.cursor() as cursor:
                    cursor.execute(
                        'SELECT 1 FROM user_store WHERE user_id = %s AND store_id = %s',
                        (user_id, store_id)
                    )
                    if cursor.fetchone():
                        logging.error(f"Store with store_id {store_id} already exists for user {user_id}.")
                        return error.error_exist_store_id(store_id)

                    cursor.execute(
                        'INSERT INTO user_store(store_id, user_id) VALUES (%s, %s)',
                        (store_id, user_id)
                    )

        except psycopg2.Error as e:
            logging.error(f"Database error while creating store: {str(e)}")
            if isinstance(e, psycopg2.IntegrityError):
                logging.error(f"IntegrityError: Likely caused by duplicate store_id and user_id.")
            return 528, "{}".format(str(e))
        except BaseException as e:
            logging.error(f"Unexpected error: {str(e)}")
            return 530, "{}".format(str(e))

        return 200, "ok"

    def send_order(self, user_id: str, store_id: str, order_id: str) -> (int, str):
        try:
            if not self.user_id_exist(user_id):
                logging.error(f"User with id {user_id} does not exist.")
                return error.error_non_exist_user_id(user_id)

            if not self.store_id_exist(store_id):
                logging.error(f"Store with id {store_id} does not exist.")
                return error.error_non_exist_store_id(store_id)

            with self.conn:
                with self.conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT order_id, order_status FROM history_order WHERE order_id = %s;",
                        (order_id,)
                    )
                    order = cursor.fetchone()
                    if not order:
                        logging.error(f"Order with id {order_id} not found.")
                        return error.error_invalid_order_id(order_id)

                    order_status = order[1]

                    if order_status == 'sent':
                        logging.warning(f"Order {order_id} is already marked as sent.")
                        return error.error_order_already_sent(order_id)

                    if order_status != 'paid':
                        logging.warning(f"Order {order_id} is not paid yet. Current status: {order_status}.")
                        return error.error_not_paid(order_id)

                    cursor.execute(
                        "UPDATE history_order SET order_status = 'sent' WHERE order_id = %s;",
                        (order_id,)
                    )
                    if cursor.rowcount == 0:
                        logging.error(f"Failed to update order {order_id}. No rows affected.")
                        return error.error_invalid_order_id(order_id)

        except psycopg2.Error as e:
            logging.error(f"Database error while sending order {order_id}: {str(e)}")
            return 528, f"Database error: {str(e)}"

        except BaseException as e:
            logging.error(f"Unexpected error while sending order {order_id}: {str(e)}")
            return 530, f"Unexpected error: {str(e)}"

        return 200, "ok"
