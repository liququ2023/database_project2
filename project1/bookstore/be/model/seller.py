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

            cursor = self.conn.cursor()
            cursor.execute(
                'INSERT INTO store(store_id, book_id, book_info, stock_level) '
                'VALUES (%s, %s, %s, %s)',
                (store_id, book_id, book_json_str, stock_level),
            )
            self.conn.commit()
        except psycopg2.Error as e:
            logging.error(f"Database error while adding book: {str(e)}")
            return 528, "{}".format(str(e))
        except BaseException as e:
            logging.error(f"Unexpected error: {str(e)}")
            return 530, "{}".format(str(e))
        finally:
            cursor.close()
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

            cursor = self.conn.cursor()
            cursor.execute(
                'UPDATE store SET stock_level = stock_level + %s '
                'WHERE store_id = %s AND book_id = %s',
                (add_stock_level, store_id, book_id),
            )
            self.conn.commit()
        except psycopg2.Error as e:
            logging.error(f"Database error while updating stock level: {str(e)}")
            return 528, "{}".format(str(e))
        except BaseException as e:
            logging.error(f"Unexpected error: {str(e)}")
            return 530, "{}".format(str(e))
        finally:
            cursor.close()
        return 200, "ok"

    def create_store(self, user_id: str, store_id: str) -> (int, str):
        try:
            # 检查 user_id 是否存在
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)

            # 在插入之前检查 store_id 是否已经存在
            if self.store_id_exist(store_id):
                return error.error_exist_store_id(store_id)

            # 检查 user_id 和 store_id 组合是否已经存在于 user_store 表中
            cursor = self.conn.cursor()
            cursor.execute(
                'SELECT 1 FROM user_store WHERE user_id = %s AND store_id = %s',
                (user_id, store_id)
            )
            if cursor.fetchone():
                logging.error(f"Store with store_id {store_id} already exists for user {user_id}.")
                return error.error_exist_store_id(store_id)

            # 执行插入操作
            cursor.execute(
                'INSERT INTO user_store(store_id, user_id) VALUES (%s, %s)',
                (store_id, user_id)
            )
            self.conn.commit()
        except psycopg2.Error as e:
            logging.error(f"Database error while creating store: {str(e)}")
            # 输出更详细的错误信息
            if isinstance(e, psycopg2.IntegrityError):
                logging.error(f"IntegrityError: Likely caused by duplicate store_id and user_id.")
            return 528, "{}".format(str(e))
        except BaseException as e:
            logging.error(f"Unexpected error: {str(e)}")
            return 530, "{}".format(str(e))
        finally:
            cursor.close()

        return 200, "ok"

