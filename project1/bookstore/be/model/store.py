import logging
import psycopg2
import threading

class Store:
    database: str

    def __init__(self, db_path):
        # PostgreSQL连接字符串，替换为实际的数据库地址、用户名和密码
        self.database = f"postgresql://postgres:Liwanting2003@localhost:5432/bookstore"
        self.init_tables()

    def init_tables(self):
        """ 初始化数据库表 """
        conn = None
        cursor = None
        try:
            logging.info("Initializing database tables...")
            conn = self.get_db_conn()
            cursor = conn.cursor()
            cursor.execute("SET client_encoding TO 'UTF8';")

            # 创建用户表
            cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS "user" (
                user_id TEXT PRIMARY KEY, 
                password TEXT NOT NULL, 
                balance INTEGER NOT NULL, 
                token TEXT, 
                terminal TEXT
            );
            """)

            # 创建用户与商店的关系表
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS "user_store" (
                user_id TEXT, 
                store_id TEXT, 
                PRIMARY KEY(user_id, store_id)
            );
            """)

            # 创建商店库存表
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS "store" ( 
                store_id TEXT, 
                book_id TEXT, 
                book_info TEXT, 
                stock_level INTEGER, 
                PRIMARY KEY(store_id, book_id)
            );
            """)

            # 创建订单表
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS "new_order" ( 
                order_id TEXT PRIMARY KEY, 
                user_id TEXT, 
                store_id TEXT
            );
            """)

            # 创建订单详情表
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS "new_order_detail" ( 
                order_id TEXT, 
                book_id TEXT, 
                count INTEGER, 
                price INTEGER,  
                PRIMARY KEY(order_id, book_id)
            );
            """)

            # 创建历史订单表
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS "history_order" ( 
                order_id TEXT PRIMARY KEY, 
                user_id TEXT, 
                store_id TEXT, 
                order_status TEXT
            );
            """)

            # 创建历史订单详情表
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS "history_order_detail" ( 
                order_id TEXT, 
                book_id TEXT, 
                count INTEGER, 
                price INTEGER,  
                PRIMARY KEY(order_id, book_id)
            );
            """)

            conn.commit()  # 提交事务
            logging.info("Database tables initialized successfully.")
        except psycopg2.Error as e:
            if conn:
                conn.rollback()  # 回滚事务
            logging.error(f"Database error during table initialization: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def get_db_conn(self) -> psycopg2.extensions.connection:
        """ 从 PostgreSQL 获取数据库连接 """
        conn = psycopg2.connect(self.database)
        return conn

# 全局变量，用于保存 Store 实例
database_instance: Store = None

# 用于同步数据库初始化的事件
init_completed_event = threading.Event()

def init_database(db_path):
    """初始化数据库，在多线程环境下同步执行"""
    global database_instance
    try:
        logging.info("Initializing the database...")
        database_instance = Store(db_path)
        init_completed_event.set()  # 通知其他线程初始化完成
        logging.info("Database initialized successfully.")
    except Exception as e:
        logging.error(f"Error during database initialization: {e}")

def get_db_conn():
    """ 获取数据库连接，确保数据库已初始化 """
    global database_instance
    # 确保数据库已初始化
    logging.info("Waiting for database initialization...")
    init_completed_event.wait()  # 等待数据库初始化完成
    logging.info("Database initialized, providing connection...")

    # 获取数据库连接
    conn = database_instance.get_db_conn()

    # 设置客户端编码为 UTF-8
    conn.set_client_encoding('UTF8')

    return conn

# 示例: 增加事务处理的操作
def add_book_to_store(store_id: str, book_id: str, book_info: str, stock_level: int):
    """ 将书籍添加到商店库存中 """
    conn = None
    cursor = None
    try:
        conn = get_db_conn()  # 获取数据库连接
        cursor = conn.cursor()

        # 插入新的书籍信息到商店库存表
        cursor.execute("""
        INSERT INTO "store" (store_id, book_id, book_info, stock_level)
        VALUES (%s, %s, %s, %s);
        """, (store_id, book_id, book_info, stock_level))

        conn.commit()  # 提交事务
        logging.info(f"Book {book_id} added to store {store_id} successfully.")
    except psycopg2.Error as e:
        if conn:
            conn.rollback()  # 回滚事务
        logging.error(f"Database error during adding book to store: {e}")
    except Exception as e:
        if conn:
            conn.rollback()  # 回滚事务
        logging.error(f"Unexpected error during adding book to store: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def update_stock_level(store_id: str, book_id: str, new_stock_level: int):
    """ 更新商店库存中的书籍数量 """
    conn = None
    cursor = None
    try:
        conn = get_db_conn()  # 获取数据库连接
        cursor = conn.cursor()

        # 更新书籍库存
        cursor.execute("""
        UPDATE "store"
        SET stock_level = %s
        WHERE store_id = %s AND book_id = %s;
        """, (new_stock_level, store_id, book_id))

        conn.commit()  # 提交事务
        logging.info(f"Stock level for book {book_id} in store {store_id} updated to {new_stock_level}.")
    except psycopg2.Error as e:
        if conn:
            conn.rollback()  # 回滚事务
        logging.error(f"Database error during updating stock level: {e}")
    except Exception as e:
        if conn:
            conn.rollback()  # 回滚事务
        logging.error(f"Unexpected error during updating stock level: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
