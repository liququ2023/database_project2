import psycopg2
from psycopg2 import sql
from be.model import store  # 假设 store.py 中包含了数据库连接相关的内容

class DBConn:
    def __init__(self):
        self.conn = store.get_db_conn()  # 假设此方法返回的是一个 PostgreSQL 连接对象

    # 检查用户ID是否存在
    def user_id_exist(self, user_id):
        cursor = None
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    "SELECT 1 FROM \"user\" WHERE user_id = %s LIMIT 1",  # 查询用户ID是否存在
                    (user_id,)
                )
                result = cursor.fetchone()
                return result is not None  # 如果查询到结果则返回True，否则返回False
        except psycopg2.Error as e:
            self.conn.rollback()  # 回滚事务
            return False
        except Exception as e:
            self.conn.rollback()  # 回滚事务
            return False

    # 检查书ID是否存在
    def book_id_exist(self, store_id, book_id):
        cursor = None
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    "SELECT 1 FROM store WHERE store_id = %s AND book_id = %s LIMIT 1",  # 查询书籍ID是否存在
                    (store_id, book_id)
                )
                result = cursor.fetchone()
                return result is not None  # 如果查询到结果则返回True，否则返回False
        except psycopg2.Error as e:
            self.conn.rollback()  # 回滚事务
            return False
        except Exception as e:
            self.conn.rollback()  # 回滚事务
            return False

    # 检查店铺ID是否存在
    def store_id_exist(self, store_id):
        cursor = None
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    "SELECT 1 FROM user_store WHERE store_id = %s LIMIT 1",  # 查询店铺ID是否存在
                    (store_id,)
                )
                result = cursor.fetchone()
                return result is not None  # 如果查询到结果则返回True，否则返回False
        except psycopg2.Error as e:
            self.conn.rollback()  # 回滚事务
            return False
        except Exception as e:
            self.conn.rollback()  # 回滚事务
            return False
