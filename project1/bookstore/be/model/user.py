import jwt
import time
import logging
import psycopg2
from be.model import error
from be.model import db_conn


# encode a json string like:
#   {
#       "user_id": [user name],
#       "terminal": [terminal code],
#       "timestamp": [ts]} to a JWT
#   }
def jwt_encode(user_id: str, terminal: str) -> str:
    encoded = jwt.encode(
        {"user_id": user_id, "terminal": terminal, "timestamp": time.time()},
        key=user_id,
        algorithm="HS256",
    )
    return encoded


# decode a JWT to a json string like:
#   {
#       "user_id": [user name],
#       "terminal": [terminal code],
#       "timestamp": [ts]} to a JWT
#   }
def jwt_decode(encoded_token, user_id: str) -> dict:
    decoded = jwt.decode(encoded_token, key=user_id, algorithms="HS256")
    return decoded


class User(db_conn.DBConn):
    token_lifetime: int = 3600  # 3600 seconds

    def __init__(self):
        db_conn.DBConn.__init__(self)

    def __check_token(self, user_id, db_token, token) -> bool:
        try:
            if db_token != token:
                return False
            jwt_text = jwt_decode(encoded_token=token, user_id=user_id)
            ts = jwt_text["timestamp"]
            if ts is not None:
                now = time.time()
                if self.token_lifetime > now - ts >= 0:
                    return True
        except jwt.exceptions.InvalidSignatureError as e:
            logging.error(f"JWT signature error: {str(e)}")
            return False
        return False

    def register(self, user_id: str, password: str):
        cursor = None
        try:
            cursor = self.conn.cursor()

            # Check if user already exists
            cursor.execute("SELECT 1 FROM \"user\" WHERE user_id = %s;", (user_id,))
            if cursor.fetchone():
                logging.error(f"User ID {user_id} already exists.")
                cursor.close()
                return error.error_exist_user_id(user_id)

            # Proceed with registration if user does not exist
            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)

            cursor.execute(
                "INSERT INTO \"user\"(user_id, password, balance, token, terminal) "
                "VALUES (%s, %s, %s, %s, %s);",
                (user_id, password, 0, token, terminal),
            )
            self.conn.commit()
        except psycopg2.Error as e:
            if cursor:
                self.conn.rollback()  # Rollback the transaction on error
            logging.error(f"Database error during register: {e.pgcode} - {e.pgerror}")
            return error.error_exist_user_id(user_id)  # Assuming this is the user already exists error
        except Exception as e:
            if cursor:
                self.conn.rollback()  # Rollback the transaction on unexpected error
            logging.error(f"Unexpected error during register: {str(e)}")
            return 500, f"Unexpected error: {str(e)}"
        finally:
            if cursor:
                cursor.close()

        return 200, "ok"

    def check_token(self, user_id: str, token: str) -> (int, str):
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT token FROM \"user\" WHERE user_id=%s;", (user_id,))
            row = cursor.fetchone()
            if row is None:
                cursor.close()
                return error.error_authorization_fail()
            db_token = row[0]
        except psycopg2.Error as e:
            if cursor:
                cursor.close()
            logging.error(f"Database error during check_token: {str(e)}")
            return 528, f"Database error: {str(e)}"
        finally:
            if cursor:
                cursor.close()

        if not self.__check_token(user_id, db_token, token):
            return error.error_authorization_fail()

        return 200, "ok"

    def check_password(self, user_id: str, password: str) -> (int, str):
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT password FROM \"user\" WHERE user_id=%s;", (user_id,))
            row = cursor.fetchone()
            if row is None:
                cursor.close()
                return error.error_authorization_fail()

            if password != row[0]:
                cursor.close()
                return error.error_authorization_fail()

        except psycopg2.Error as e:
            if cursor:
                cursor.close()
            logging.error(f"Database error during check_password: {str(e)}")
            return 528, f"Database error: {str(e)}"
        finally:
            if cursor:
                cursor.close()

        return 200, "ok"

    def login(self, user_id: str, password: str, terminal: str) -> (int, str, str):
        token = ""
        cursor = None
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message, ""

            token = jwt_encode(user_id, terminal)

            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE \"user\" SET token = %s, terminal = %s WHERE user_id = %s;",
                (token, terminal, user_id),
            )
            if cursor.rowcount == 0:
                cursor.close()
                return error.error_authorization_fail() + ("",)
            self.conn.commit()
        except psycopg2.Error as e:
            if cursor:
                self.conn.rollback()  # Rollback the transaction on error
            logging.error(f"Database error during login: {str(e)}")
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            if cursor:
                self.conn.rollback()  # Rollback the transaction on unexpected error
            logging.error(f"Unexpected error during login: {str(e)}")
            return 530, "{}".format(str(e)), ""
        finally:
            if cursor:
                cursor.close()

        return 200, "ok", token

    def logout(self, user_id: str, token: str) -> bool:
        cursor = None
        try:
            code, message = self.check_token(user_id, token)
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            dummy_token = jwt_encode(user_id, terminal)

            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE \"user\" SET token = %s, terminal = %s WHERE user_id = %s;",
                (dummy_token, terminal, user_id),
            )
            if cursor.rowcount == 0:
                cursor.close()
                return error.error_authorization_fail()

            self.conn.commit()
        except psycopg2.Error as e:
            if cursor:
                self.conn.rollback()  # Rollback the transaction on error
            logging.error(f"Database error during logout: {str(e)}")
            return 528, "{}".format(str(e))
        except BaseException as e:
            if cursor:
                self.conn.rollback()  # Rollback the transaction on unexpected error
            logging.error(f"Unexpected error during logout: {str(e)}")
            return 530, "{}".format(str(e))
        finally:
            if cursor:
                cursor.close()

        return 200, "ok"

    def unregister(self, user_id: str, password: str) -> (int, str):
        cursor = None
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message

            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM \"user\" WHERE user_id=%s;", (user_id,))
            if cursor.rowcount == 1:
                self.conn.commit()
            else:
                cursor.close()
                return error.error_authorization_fail()
        except psycopg2.Error as e:
            if cursor:
                self.conn.rollback()  # Rollback the transaction on error
            logging.error(f"Database error during unregister: {str(e)}")
            return 528, "{}".format(str(e))
        except BaseException as e:
            if cursor:
                self.conn.rollback()  # Rollback the transaction on unexpected error
            logging.error(f"Unexpected error during unregister: {str(e)}")
            return 530, "{}".format(str(e))
        finally:
            if cursor:
                cursor.close()

        return 200, "ok"

    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        cursor = None
        try:
            code, message = self.check_password(user_id, old_password)
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)

            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE \"user\" SET password = %s, token = %s, terminal = %s WHERE user_id = %s;",
                (new_password, token, terminal, user_id),
            )
            if cursor.rowcount == 0:
                cursor.close()
                return error.error_authorization_fail()

            self.conn.commit()
        except psycopg2.Error as e:
            if cursor:
                self.conn.rollback()  # Rollback the transaction on error
            logging.error(f"Database error during change_password: {str(e)}")
            return 528, "{}".format(str(e))
        except BaseException as e:
            if cursor:
                self.conn.rollback()  # Rollback the transaction on unexpected error
            logging.error(f"Unexpected error during change_password: {str(e)}")
            return 530, "{}".format(str(e))
        finally:
            if cursor:
                cursor.close()

        return 200, "ok"

    def search_book(self, title='', content='', tag='', store_id=''):
        cursor = None
        try:
            cursor = self.conn.cursor()  # 使用 conn 来创建游标
            query_parts = []  # 用于存储查询条件
            params = []  # 用于存储查询参数

            # 根据输入条件构建查询
            if title:
                query_parts.append("b.title LIKE %s")
                params.append(f"%{title}%")
            if content:
                query_parts.append("b.content LIKE %s")
                params.append(f"%{content}%")
            if tag:
                query_parts.append("b.tags LIKE %s")
                params.append(f"%{tag}%")

            # 如果有 store_id，查询该商店下的所有书籍 ID
            if store_id:
                # 查询商店中的所有书籍 ID
                store_query = """
                    SELECT book_id FROM store WHERE store_id = %s;
                """
                cursor.execute(store_query, (store_id,))
                store_result = cursor.fetchall()

                if not store_result:
                    return 528, f"Store with ID {store_id} does not exist.", []  # 返回商店不存在

                book_ids = [item[0] for item in store_result]  # 提取所有 book_id

                if not book_ids:  # 如果商店中没有书籍
                    return 528, f"No books found in store with ID {store_id}.", []  # 返回商店内没有书籍

                # 构造 IN 查询条件
                query_parts.append(f"b.id IN ({','.join(['%s'] * len(book_ids))})")
                params.extend(book_ids)

            # 拼接最终的查询条件
            where_clause = " AND ".join(query_parts) if query_parts else "1=1"

            # 拼接最终的查询语句
            sql = f"""
                SELECT b.id, b.title, b.content, b.tags 
                FROM books b
                WHERE {where_clause};
            """
            cursor.execute(sql, tuple(params))  # 使用 tuple 将所有参数传递给 execute
            results = cursor.fetchall()

            # 如果没有找到符合条件的书籍
            if not results:
                return 528, "No books found matching the criteria.", []

            # 如果没有指定 store_id，返回找到的书籍（即不管它是否在商店中）
            if not store_id:
                return 200, "ok", results

            # 如果指定了 store_id，检查每本书是否属于该商店
            for book in results:
                book_id = book[0]  # 获取书籍的 ID
                cursor.execute(""" 
                    SELECT 1 FROM store WHERE book_id = %s AND store_id = %s
                """, (book_id, store_id))
                store_check = cursor.fetchone()
                if not store_check:
                    return 528, f"Book '{book[1]}' not found in store with ID {store_id}.", []

            # 如果书籍都属于指定的商店
            return 200, "ok", results

        except psycopg2.Error as e:
            if cursor:
                self.conn.rollback()  # Rollback the transaction on error
            logging.error(f"Database error occurred: {e.pgcode}, {e.pgerror}")  # 输出具体错误
            return 528, f"Database error occurred: {e.pgcode}, {e.pgerror}", []

        except Exception as e:
            if cursor:
                self.conn.rollback()  # Rollback the transaction on unexpected error
            logging.error(f"Unexpected error occurred: {str(e)}")  # 输出具体错误
            return 530, f"Unexpected error occurred: {str(e)}", []

        finally:
            if cursor:
                cursor.close()  # 确保游标总是被关闭
