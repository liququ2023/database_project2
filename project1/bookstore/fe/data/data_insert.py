import sqlite3
import psycopg2
from psycopg2 import sql, Binary
import os

# SQLite 数据库路径
sqlite_db_path = 'book.db'
print(f"Connecting to SQLite database at: {sqlite_db_path}")

# PostgreSQL 数据库连接信息
postgres_host = "localhost"
postgres_db = "bookstore"
postgres_user = "postgres"
postgres_password = "Liwanting2003"


# 连接到 SQLite 数据库
try:
    conn = sqlite3.connect(sqlite_db_path)
    cursor = conn.cursor()

    # 查询所有书籍信息，包括图片数据
    cursor.execute("SELECT * FROM book")
    books = cursor.fetchall()

    # 打印查询结果
    print(f"Retrieved {len(books)} books from SQLite")

    # 获取列名
    column_names = [description[0] for description in cursor.description]

    # 将数据转换为字典格式
    books_list = [dict(zip(column_names, book)) for book in books]
    print(f"Books List: {books_list[:5]}")  # 打印前5本书以检查

except sqlite3.Error as e:
    print(f"SQLite error: {e}")
finally:
    # 关闭 SQLite 连接
    if conn:
        conn.close()

# 连接到 PostgreSQL 数据库
pg_conn = None
pg_cursor = None
try:
    pg_conn = psycopg2.connect(
        host=postgres_host,
        dbname=postgres_db,
        user=postgres_user,
        password=postgres_password
    )
    pg_cursor = pg_conn.cursor()

    # 开始事务
    pg_conn.autocommit = False  # 关闭自动提交，显式管理事务

    # 创建表 (如果表不存在)
    create_table_query = """
    CREATE TABLE IF NOT EXISTS books (
        id TEXT PRIMARY KEY,
        title TEXT,
        author TEXT,
        publisher TEXT,
        original_title TEXT,
        translator TEXT,
        pub_year TEXT,
        pages INTEGER,
        price INTEGER,
        currency_unit TEXT,
        binding TEXT,
        isbn TEXT,
        author_intro TEXT,
        book_intro TEXT,
        content TEXT,
        tags TEXT,
        picture BYTEA  -- 用于存储图片的二进制数据
    );
    """
    pg_cursor.execute(create_table_query)
    pg_conn.commit()
    print("Table created successfully.")

    # 插入数据到 PostgreSQL
    if books_list:  # 检查book_list是否为空
        for book in books_list:
            try:
                # 获取 SQLite 中的图片二进制数据
                picture_data = book.get('picture')
                # picture_data 是二进制数据，如果它是 None 或空，则跳过
                if picture_data:
                    print(f"Inserting book with ID: {book['id']}, Picture Data Length: {len(picture_data)}")
                else:
                    print(f"No picture data for book ID: {book['id']}")

                # 插入数据
                insert_query = sql.SQL("""
                    INSERT INTO books (
                        id, title, author, publisher, original_title, translator, pub_year,
                        pages, price, currency_unit, binding, isbn, author_intro, book_intro,
                        content, tags, picture
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING  -- 如果有相同的 id，则跳过
                """)

                pg_cursor.execute(insert_query, (
                    book['id'],
                    book['title'],
                    book['author'],
                    book['publisher'],
                    book['original_title'],
                    book['translator'],
                    book['pub_year'],
                    book['pages'],
                    book['price'],
                    book['currency_unit'],
                    book['binding'],
                    book['isbn'],
                    book['author_intro'],
                    book['book_intro'],
                    book['content'],
                    book['tags'],
                    Binary(picture_data) if picture_data else None
                ))

                print(f"Inserted book with id: {book['id']}")

            except Exception as e:
                print(f"Error inserting book with id {book['id']}: {e}")
                print(f"Failed Book Data: {book}")
                pg_conn.rollback()  # 如果插入失败，回滚本次操作

    # 提交所有插入操作
    pg_conn.commit()
    print("Data migration completed successfully.")

except psycopg2.Error as e:
    print(f"PostgreSQL error: {e}")
    pg_conn.rollback()  # 如果发生任何异常，回滚事务
finally:
    # 关闭 PostgreSQL 连接
    if pg_cursor:
        pg_cursor.close()
    if pg_conn:
        pg_conn.close()
