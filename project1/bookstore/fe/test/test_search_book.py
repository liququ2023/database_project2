import pytest
import random
from be.model.user import User
import psycopg2
from fe.access import book
from fe.access import auth
from fe import conf
import logging


class TestSearchBook:
    def setup_method(self):
        # 初始化 User 实例和数据库连接
        self.auth = User()  # 假设 User 类继承自 DBConn

        # 随机选择一个商店的 ID
        self.store_id = self._fetch_random_store_id()

        # 从数据库中加载书籍信息
        self.books = self._fetch_books_from_db()

        # 获取第一个书籍的标题、内容和标签作为测试数据
        self.title_in_store = self.books[0]['title']
        self.content_in_store = self.books[0]['content']
        self.tag_in_store = self.books[0]['tags'][0]


    def _fetch_random_store_id(self):
        # 从数据库中获取所有商店的 ID
        cursor = self.auth.conn.cursor()
        cursor.execute("SELECT store_id FROM store;")  # 假设商店表有 store_id 字段
        store_ids = cursor.fetchall()
        cursor.close()

        if store_ids:
            # 随机选择一个商店 ID
            return random.choice(store_ids)[0]  # 假设 store_id 存在第一列
        else:
            raise ValueError("No store IDs found in the database.")

    def _fetch_books_from_db(self):
        # 从数据库中获取书籍列表
        cursor = self.auth.conn.cursor()
        cursor.execute("SELECT id, title, content, tags FROM books;")  # 确保查询包含 book_id
        books = cursor.fetchall()
        cursor.close()

        # 返回的每个书籍是一个 tuple: (book_id, title, content, tags)
        # 将 tags 字段从字符串转为列表，并确保返回每本书的 book_id
        return [{"id": book[0], "title": book[1], "content": book[2], "tags": book[3].split('\n')} for book in
                books]

    def test_search_in_store(self):
        # 使用 title 查询商店中的书籍
        response_code, message, results = self.auth.search_book(title=self.title_in_store, store_id=self.store_id)
        print(f"Searching by title: Response code: {response_code}, Message: {message}, Results: {results}")
        assert response_code == 200, f"Expected 200, got {response_code} for title search"

        # 使用 content 查询商店中的书籍
        response_code, message, results = self.auth.search_book(content=self.content_in_store, store_id=self.store_id)
        print(f"Searching by content: Response code: {response_code}, Message: {message}, Results: {results}")
        assert response_code == 200, f"Expected 200, got {response_code} for content search"

        # 使用 tag 查询商店中的书籍
        response_code, message, results = self.auth.search_book(tag=self.tag_in_store, store_id=self.store_id)
        print(f"Searching by tag: Response code: {response_code}, Message: {message}, Results: {results}")
        assert response_code == 200, f"Expected 200, got {response_code} for tag search"

        # 使用 title 和 content 组合查询
        response_code, message, results = self.auth.search_book(title=self.title_in_store,
                                                                content=self.content_in_store, store_id=self.store_id)
        print(f"Searching by title and content: Response code: {response_code}, Message: {message}, Results: {results}")
        assert response_code == 200, f"Expected 200, got {response_code} for title and content search"

        # 使用 title 和 tag 组合查询
        response_code, message, results = self.auth.search_book(title=self.title_in_store, tag=self.tag_in_store,
                                                                store_id=self.store_id)
        print(f"Searching by title and tag: Response code: {response_code}, Message: {message}, Results: {results}")
        assert response_code == 200, f"Expected 200, got {response_code} for title and tag search"

        # 使用 content 和 tag 组合查询
        response_code, message, results = self.auth.search_book(content=self.content_in_store, tag=self.tag_in_store,
                                                                store_id=self.store_id)
        print(f"Searching by content and tag: Response code: {response_code}, Message: {message}, Results: {results}")
        assert response_code == 200, f"Expected 200, got {response_code} for content and tag search"

        # 使用 title, content, 和 tag 组合查询
        response_code, message, results = self.auth.search_book(title=self.title_in_store,
                                                                content=self.content_in_store, tag=self.tag_in_store,
                                                                store_id=self.store_id)
        print(
            f"Searching by title, content, and tag: Response code: {response_code}, Message: {message}, Results: {results}")
        assert response_code == 200, f"Expected 200, got {response_code} for title, content, and tag search"

    def test_search_global(self):
        for b in self.books:
            test_title = b['title']
            test_content = b['content'].split("\n")[0]
            test_tag = b['tags'][random.randint(0, len(b['tags']) - 1)]

            # 调用 search_book 方法进行测试
            response_code, message, results = self.auth.search_book(title=test_title)
            print(f"Response code: {response_code}, Message: {message}, Results: {results}")  # 打印调试信息
            assert response_code == 200, f"Expected 200, got {response_code} for title: {test_title}"

    def test_search_global_not_exists(self):
        test_title = "test_title"
        test_content = "test_content"
        test_tag = "test_tag"

        # 测试不存在的书籍信息
        response_code, message, results = self.auth.search_book(title=test_title)
        assert response_code == 528, f"Expected 528, got {response_code} for non-existing title"

    def test_search_not_exist_store_id(self):
        test_title = self.books[0]['title']  # 从数据库中获取的第一个书籍标题
        invalid_store_id = 'non_existent_store_id'  # 假设这是一个不存在的 store_id

        # 测试使用不存在的 store_id 查找书籍信息
        response_code, message, results = self.auth.search_book(title=test_title, store_id=invalid_store_id)

        # 验证是否返回了 528 错误码，说明商店不存在
        assert response_code == 528, f"Expected 528, got {response_code} for non-existent store ID"
        assert "does not exist" in message, f"Unexpected message: {message}"

    def test_search_not_in_store(self):
        # 获取所有在商店内的书籍 book_id
        book_ids_in_store = [b['id'] for b in self.books]
        cursor = self.auth.conn.cursor()
        cursor.execute(""" 
            SELECT book_id, book_info
            FROM store 
            WHERE book_id NOT IN %s;
        """, (tuple(book_ids_in_store),))
        not_in_store_books = cursor.fetchall()
        cursor.close()

        # 如果有书籍不在商店中，进行测试
        if not_in_store_books:
            random_not_in_store_book = random.choice(not_in_store_books)
            test_title = json.loads(random_not_in_store_book[1])['title']

            # 查询不在商店中的书籍
            response_code, message, results = self.auth.search_book(title=test_title)
            print(
                f"Searching by title not in store: Response code: {response_code}, Message: {message}, Results: {results}")

            # 期望返回 528，因为书籍不在商店中
            assert response_code == 528, f"Expected 528, got {response_code} for title not in store"
        else:
            pytest.skip("No books found that are not in the store.")
