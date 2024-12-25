import psycopg2
import random
import base64
import json


class Book:
    id: str
    title: str
    author: str
    publisher: str
    original_title: str
    translator: str
    pub_year: str
    pages: int
    price: int
    currency_unit: str
    binding: str
    isbn: str
    author_intro: str
    book_intro: str
    content: str
    tags: [str]
    pictures: [bytes]

    def __init__(self):
        self.tags = []
        self.pictures = []


class BookDB:
    def __init__(self, large: bool = False):
        """
        初始化数据库连接和参数设置。
        :param large: 是否获取更多的书籍图片，默认为 False。
        """
        self.large = large  # 将 large 参数存储为实例变量
        self.conn = psycopg2.connect(
            dbname="bookstore",  # 替换为你的数据库名
            user="postgres",     # 替换为你的用户名
            password="Liwanting2003",  # 替换为你的密码
            host="localhost",    # 主机地址
            port="5432",         # 端口号
            options="-c client_encoding=UTF8"  # 强制设置客户端编码为 UTF8
        )
        self.cursor = self.conn.cursor()

    def get_book_count(self):
        """
        获取书籍总数
        :return: 书籍总数
        """
        self.cursor.execute("SELECT count(id) FROM books")
        row = self.cursor.fetchone()
        return row[0]

    def get_book_info(self, start, size) -> [Book]:
        """
        获取书籍信息，包括书名、作者、出版商等信息。
        :param start: 开始的偏移量
        :param size: 每次获取的书籍数量
        :return: 包含书籍信息的 Book 对象列表
        """
        books = []
        self.cursor.execute(
            """
            SELECT id, title, author, publisher, original_title, translator, pub_year, 
                   pages, price, currency_unit, binding, isbn, author_intro, book_intro, 
                   content, tags, picture 
            FROM books 
            ORDER BY id
            LIMIT %s OFFSET %s
            """,
            (size, start)
        )

        for row in self.cursor.fetchall():
            book = Book()
            book.id = row[0]
            book.title = row[1]
            book.author = row[2]
            book.publisher = row[3]
            book.original_title = row[4]
            book.translator = row[5]
            book.pub_year = row[6]
            book.pages = row[7]
            book.price = row[8]
            book.currency_unit = row[9]
            book.binding = row[10]
            book.isbn = row[11]
            book.author_intro = row[12]
            book.book_intro = row[13]
            book.content = row[14]
            tags = row[15]
            picture = row[16]

            # 处理标签
            for tag in tags.split("\n"):
                if tag.strip() != "":
                    book.tags.append(tag)

            # 根据 large 参数决定是否添加更多图片
            if self.large:
                # 如果 large 为 True，随机添加更多图片
                for i in range(0, random.randint(3, 9)):  # 假设更多图片是随机 3 到 9 张
                    if picture is not None:
                        encode_str = base64.b64encode(picture).decode("utf-8")
                        book.pictures.append(encode_str)
            else:
                # 如果 large 为 False，只添加较少的图片，或者不添加
                if picture is not None:
                    encode_str = base64.b64encode(picture).decode("utf-8")
                    book.pictures.append(encode_str)

            books.append(book)

        return books
