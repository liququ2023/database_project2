# 数据库项目二：书店实验报告
---
作者：李婉婷   10225501449
## 一，项目简介
### 项目成员
#### 姓名：李婉婷   年纪：22级   学号：10225501449
### 项目内容介绍
此项目为课程当代数据管理系统的第二次大作业bookstore。

该项目要求实现一个提供网上购书功能的网站后端。网站支持书上在上面开商店，购买者可以通过网站购买。买家和买家都可以注册自己的账号。一个卖家可以开一个或者多个网上商店。买家可以为自己的账户充值，在任意商店购买图书。

核心数据库使用postgresql

此项目支持 下单->付款->发货->收货 流程。

## 二，新bookstore_postgresql项目目录结构
bookstore_postgresql的目录结构与提供的demo每个部分的功能保持一致，在原本的mongodb项目的基础上进行代码修改，用于实现数据库操作的迁移或者新功能。
```
bookstore_postgresql
  |-- be                            后端
        |-- model                     后端逻辑代码
        |-- view                      访问后端接口
        |-- ....
  |-- doc                           JSON API规范说明
  |-- fe                            前端访问与测试代码
        |-- access
        |-- bench                     效率测试
        |-- data                    
            |-- book.db                 原sqlite数据
            |-- scraper.py              从豆瓣爬取的图书信息数据的代码
            |-- data_insert             数据迁移
        |-- test                      功能性测试（包含对前60%功能的测试，不要修改已有的文件，可以提pull request或bug）
        |-- conf.py                   测试参数，修改这个文件以适应自己的需要
        |-- conftest.py               pytest初始化配置，修改这个文件以适应自己的需要
        |-- ....
  |-- ....
```
## 三，关系数据库设计：关系型 schema
### 前60%功能的文档结构设计：
#### ER图如下：
![ER](ER.PNG)

由于此项目是要把原来基于mongodb的功能迁移到postgresql上面，且项目要求测试文件保持不变，因此，我们并不改变原来的数据存储结构，我们迁移后的每个postgresql的table中存放一个mongodb文档集合的内容，这是因为本来我们的mongodb就是基于sqlite迁移过来的，本来就是适合存放在关系模型中，同时这样的设计也更加便于我们编写业务逻辑代码。
同时我此处将BLOB数据转变为二进制数据，依旧存放在我们的postgresql数据库中
因此前60%功能的关系schema如下：
#### table1:books
- id TEXT
- title TEXT
- author TEXT
- publisher TEXT
- original_title TEXT
- translator TEXT
- pub_year TEXT
- pages INTEGER
- price INTEGER
- currency_unit TEXT
- binding TEXT
- isbn TEXT
- author_intro TEXT
- book_intro TEXT
- content TEXT
- tags TEXT
- picture BYTEA

#### table2:user
- user_id TEXT
- password TEXT
- balance INT
- token TEXT
- terminal TEXT

#### table3:user_store
- user_id TEXT
- store_id TEXT

#### table4:store
- store_id TEXT
- book_id TEXT
- book_info TEXT
- stock_level INT

#### table5:new_order
- order_id TEXT
- user_id TEXT
- store_id TEXT

#### table6:new_order_detail
- order_id TEXT
- book_id TEXT
- count INT
- price INT

### 后40%功能的文档结构设计：
唯一需要增加的就是两个表用来存储用户的历史订单：
#### table7:history_order_detail
- order_id TEXT
- user_id TEXT
- store_id TEXT
- order_status TEXT
- ##### 包含订单状态

#### table8:history_order_detail
- order_id TEXT
- book_id TEXT
- count INT
- price INT

## 四，bookstore_postgresql文档结构解析
### be目录下存放所有后端代码：

    |-- be                          后端
        |-- model                     后端逻辑代码
        |-- view                      访问后端接口
        |-- app.py
        |-- serve.py

#### model目录：实现后端接口的逻辑代码
其中包含了各个后端接口实现的逻辑代码

        |-- model
            |-- buyer.py
            |-- db-conn.py
            |-- error.py
            |-- seller.py
            |-- store.py
            |-- user.py

- buyer.py文件实现和买家有关的逻辑代码，包括实现下单，付款，充值，在本项目中新增了查看历史订单，取消订单，和确认收货功能

- db-conn.py文件封装数据库连接并提供了一些常用的查询功能，使得在代码其他部分检查用户、书籍和商店的存在性变得简单和方便，此处没有新功能的加入

- error.py文件定义了一些错误码和相应的错误处理函数，用于在系统中返回特定的错误信息，在这里为新的功能增加新的错误码和错误处理函数

- seller.py文件实现和卖家有关的后端逻辑代码，包括实现书籍的添加，库存的更新和商店的创造，本项目新增了发货功能

- store.py用于管理与 postgresql 数据库的连接以及集合的初始化，此处没有新功能的加入

- user.py文件实现和用户有关操作的逻辑代码，包括注册，登录，登出，注销账号，修改密码功能，本项目新增搜索图书功能

*在该目录下，在每个部分中无论是否增加新功能，需要将原本基于mongodb的语句迁移到基于postgresql的语句。*
#### view目录
该目录下是后端接口的实现，分别是用户后端接口，买家后端接口和买家后端接口。此部分代码提供了 HTTP 路由，每个接口函数在接收到客户端请求后，解析参数并调用相对应的类的方法，这些方法定义在model目录中。

        |-- view
            |-- auth.py
            |-- buyer.py
            |-- seller.py

- auth.py文件提供用户相关功能的接口，包括：登录，登出，注册，注销，修改秘密，新增书籍查询接口。

- buyer.py文件提供买家相关功能的接口，包括新订单，支付订单，增加余额，新增查询历史订单，取消订单，确认收货这三个接口

- seller.py文件提供卖家相关功能的接口，包括创建商店、添加书籍以及增加库存，新增发货功能。
*该目录的文件仅提供接口和路由，与项目基于的数据库无关，因此代码无需修改，只需要为新的功能增加新的接口。*
#### app.py和server.py文件：启动后端服务器
server.py设置和启动一个 Flask web 服务器，并提供了一个用于关闭服务器的接口。
app.py启动一个名为 serve 的模块中的 be_run 函数。
app.py 是项目的入口点，负责导入 server.py 中定义的 Flask 应用，并调用 be_run 函数来启动服务器。
### fe目录下存放所有的前端代码：

    |-- fe                            前端访问与测试代码
        |-- access
        |-- bench                     效率测试
        |-- data                    
            |-- book.db                 
            |-- scraper.py              从豆瓣爬取的图书信息数据的代码
        |-- test                      功能性测试（包含对前60%功能的测试，不要修改已有的文件，可以提pull request或bug）
        |-- conf.py                   测试参数，修改这个文件以适应自己的需要
        |-- conftest.py               pytest初始化配置，修改这个文件以适应自己的需要
        |-- ....

#### access：实现前端请求发起

        |-- access
            |-- auth.py
            |-- book.py
            |-- buyer.py
            |-- new_buyer.py
            |-- new_seller.py
            |-- seller.py
            
- auth.py文件实现了用户请求的发起，包括登录，注册，修改密码，登出，注销账号的请求发起，在此项目中新增搜索书籍请求的生成。

- book.py文件用于管理书籍信息，特别是与数据库的交互。此处没有新增功能，但也因为有与数据库交互的内容，因此需要修改代码为基于postgresql的。

- buyer.py文件实现买家请求的发起，包括创建新订单，支付订单，账户充值，在这个项目中新增获取历史订单，取消订单和确认收货功能。

- new_buyer.py文件用于注册一个新的买家

- new_seller.py文件用于注册一个新的卖家

- seller.py文件实现卖家请求的发起，包括创建店铺，增加书籍，增加书籍库存，在这个项目中新增发货功能。

*该目录下的文件除了book.py文件有基于mongodb的代码，需要进行代码迁移，其余代码均为前端请求发起文件，与数据库无关，只需要仿照上面的写法增加新功能即可。*

#### bench
*此部分用于效率测试，与基于的数据库无关不用修改*
#### data
data目录下是与数据爬取和迁移有关的代码，在这里我新增了两个代码文件

        |-- data                    
            |-- book.db                 原sqlite数据
            |-- scraper.py              从豆瓣爬取的图书信息数据的代码
            |-- data_insert.py             数据迁移

我新增的代码文件：

- data_insert.py：用于将数据从book.db导出并插入到本地postgresql数据库 

#### test
test目录下是项目测试内容

        |-- test                    
            |-- ....                 
            |-- test_cancel_order
            |-- test_get_history_order
            |-- test_search_book
            |-- test_send_order

除去已有的测试文件增加了四个文件用于测试新功能。

#### conf.py和conftest.py文件:测试参数与初始化
conf.py用于测试参数设置，conftest.py是pytest初始化配置，在测试开始时自动启动后端服务，并在测试结束时安全地关闭它。通过在 pytest_configure 中等待数据库初始化完成，可以确保测试的稳定性和一致性，避免因后端未准备好而导致的测试失败。

#### 总结以上，由于是基于mongodb进行修改，因此其实前后端接口和测试代码都基本不需要修改（在我的实践中这部分只有和搜索有关的测试代码需要修改），主要修改集中在后端的model和前端的book.py，有涉及与数据库交互的步骤

## 项目准备工作
### 项目环境准备
开始工作前我们需要：
- 建造本地仓库便于使用git进行版本管理

- 启动和连接本地postgresql数据库，以便接受对于文档数据库的操作

- 下载pgAdmin4，可视化文档数据库，便于功能实现
### 数据迁移：从sqlite到postgresql
由于本来的实现是基于sqlite数据库，在进行代码的迁移之前，我们要先将数据迁移到postgresql。
如上所述，我们用于数据迁移的代码是位于前端部分data文件夹内的data_insert.py。

使用 sqlite3.connect 连接到 SQLite 数据库，创建游标对象 cursor。
通过 cursor.execute("SELECT * FROM book") 执行查询，获取所有书籍数据。
cursor.fetchall() 获取查询结果，将其存入 books。
使用 cursor.description 获取列名，将查询结果转换为字典格式，以便后续操作。
打印出前 5 本书的内容，以便检查。
```angular2html
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
```
使用 psycopg2.connect 连接到 PostgreSQL 数据库。
创建游标 pg_cursor，并关闭自动提交模式，以便管理事务。

```
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
```
创建 PostgreSQL 表
```
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
```
 插入数据到 PostgreSQL
```
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
```


## 项目具体功能实现
### 项目功能实现流程
在我们具体实现每个功能之前，在这里先阐释一下每个接口实现的细节。从前面板块的分析我们可以知道，测试文件通过前端fe/access路径下的文件来向后端发起请求，后端接口be/view路由，识别请求，并且调用后端逻辑代码be/model中对应的函数，来处理请求，与数据库交互，并且返回最终的结果，也返回状态码给前端。以上便是完整的功能实现的一个流程，我们对于每个功能基于此进行改动。
mongodb文档集合比较灵活，不需要提前写代码生成，如果在插入时不存在，会自动生成集合。
### 前60%功能的实现
#### 用户权限接口：
与用户相关的代码在前端（发起请求）：fe/access/auth，前端代码前60%的代码不需要改动，前端在定义Auth类时初始化方法接受一个 URL 前缀,将URL前缀与 "auth/" 组合，形成完整的认证 URL，便于后续的url生成。
```
    def __init__(self, url_prefix):
        self.url_prefix = urljoin(url_prefix, "auth/")
```
后端（路由）：be/view/auth:
flask：定义flask蓝图
```
bp_auth = Blueprint("auth", __name__, url_prefix="/auth")
```
后端这部分代码也不用修改，与数据库操作无关，增加新功能则需要增加新的路由。
后端（逻辑代码实现）：be/model/user
y与用户权限有关，那么首先要定义一个函数用于生成一个Token，它会根据给定的 user_id、terminal 和 secret_key 创建一个包含用户 ID、终端信息、时间戳和过期时间的加密令牌。这个令牌可以用于验证用户身份和管理会话：
```
def jwt_encode(user_id: str, terminal: str) -> str:
    encoded = jwt.encode(
        {"user_id": user_id, "terminal": terminal, "timestamp": time.time()},
        key=user_id,
        algorithm="HS256",
    )
    return encoded.encode("utf-8").decode("utf-8")
```
其次定义用于解码Token的函数：
```
def jwt_decode(encoded_token, user_id: str) -> str:
    decoded = jwt.decode(encoded_token, key=user_id, algorithms="HS256")
    return decoded
```
这部分代码定义了一个User类，包含与用户权限相关的逻辑代码，后续涉及大量与数据库的交互的方法，需要就每个功能进行修改，下面详细解释：

- #### 用户注册
前端请求发起：
```
    def register(self, user_id: str, password: str) -> int:
        """
        实现注册请求
        :param user_id: 接受的用户id
        :param password: 接受的用户密码
        发送POST请求
        :return:HTTP状态码
        """
        json = {"user_id": user_id, "password": password}
        url = urljoin(self.url_prefix, "register")
        r = requests.post(url, json=json)
        return r.status_code
```
上面使用了user_id, password形成请求体和url，发送POST请求，等待返回状态码。
该请求会被路由到：be/view/auth中的：
```
@bp_auth.route("/register", methods=["POST"])
def register():
    user_id = request.json.get("user_id", "")
    password = request.json.get("password", "")
    u = user.User()
    code, message = u.register(user_id=user_id, password=password)
    return jsonify({"message": message}), code
```
从请求的 JSON 数据中获取user_id和password。创建一个User类的实例u，然后调用其register方法，传入user_id和password。该方法返回一个状态码code和消息message。使用jsonify将消息封装成 JSON 格式，并返回给客户端，同时包含相应的状态码。
调用be/model/user中的register方法：

先检查用户是否已经存在：使用 self.conn['user'].find_one({"user_id": user_id}) 查询数据库，检查是否已有相同 user_id 的用户。如果找到了现有用户，调用 error.error_exist_user_id(user_id) 返回错误信息。

如果用户不存在，注册新用户：生成一个终端标识符 terminal，调用 jwt_encode(user_id, terminal) 函数生成一个 JWT 令牌，并将其存储在变量 token 中。创建一个字典 user_doc，包含用户的 user_id、password、初始余额（balance 为 0）、生成的 token 和 terminal。使用 self.conn['user'].insert_one(user_doc) 将新用户的文档插入到数据库中。

如果在插入过程中发生 MongoDB 相关的错误，会捕获异常并返回状态码 528 和错误信息。如果注册成功，返回状态码 200 和消息 "ok"。

数据库插入操作:
```
token = jwt_encode(user_id, terminal)
            user_doc = {
                "user_id": user_id,
                "password": password,
                "balance": 0,
                "token": token,
                "terminal": terminal
            }
            self.conn['user'].insert_one(user_doc)
```

- #### 用户登录
前端请求发起：
```
    def login(self, user_id: str, password: str, terminal: str) -> (int, str):
        """
        实现登录请求
        :param user_id: 接收的用户id
        :param password: 接收的用户密码
        :param terminal: 接收到的终端信息
        发送POST请求
        :return: HTTP状态码，从json数据中提取token，用于后续请求的身份验证
        """
        # json是请求体
        json = {"user_id": user_id, "password": password, "terminal": terminal}
        url = urljoin(self.url_prefix, "login")
        # 发送请求
        r = requests.post(url, json=json)
        return r.status_code, r.json().get("token")
```
上面使用了user_id, password, terminal形成请求体和url，发送POST请求，等待返回状态码。
该请求会被路由到be/view/auth中，这部分逻辑和上面的一样：
```
@bp_auth.route("/login", methods=["POST"])
def login():
    user_id = request.json.get("user_id", "")
    password = request.json.get("password", "")
    terminal = request.json.get("terminal", "")
    u = user.User()
    code, message, token = u.login(
        user_id=user_id, password=password, terminal=terminal
    )
    return jsonify({"message": message, "token": token}), code
```
其次调用be/model/user中的login：
```
    def login(self, user_id: str, password: str, terminal: str) -> (int, str, str):
        token = ""
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message, ""

            token = jwt_encode(user_id, terminal)
            result = self.conn['user'].update_one({'user_id': user_id}, {'$set': {'token': token, 'terminal': terminal}})
            if result.matched_count == 0:
                return error.error_authorization_fail() + ("",)
        except pymongo.errors.PyMongoError as e:
            return 528, str(e), ""
        except BaseException as e:
            return 530, "{}".format(str(e)), ""
        return 200, "ok", token
```
创建一个空字符串 token，用于存储生成的 JWT 令牌。调用 self.check_password(user_id, password) 验证用户的 user_id 和 password。如果返回的状态码 code 不等于 200，表示密码验证失败，直接返回相应的状态码和消息，同时返回空字符串作为令牌。如果密码验证通过，调用 jwt_encode(user_id, terminal) 生成 JWT 令牌，并将其赋值给 token。

使用 self.conn['user'].update_one() 方法更新数据库中该用户的 token 和 terminal 信息。如果没有找到匹配的用户（即 result.matched_count 为 0），调用 error.error_authorization_fail() 返回授权失败的错误信息，并附加一个空字符串。

如果在数据库操作过程中发生 MongoDB 相关的错误，会捕获异常并返回状态码 528 和错误信息，同时令牌为空。也有一个通用的异常处理，捕获其他可能的错误，返回状态码 530 和错误信息。

如果登录成功，返回状态码 200、消息 "ok" 和生成的 JWT 令牌。
- #### 用户登出
前端请求发起：
```
    def logout(self, user_id: str, token: str) -> int:
        """
        用户登出
        :param user_id:接受的用户id
        :param token:用户的身份验证令牌
        :return:HTTP状态码
        """
        json = {"user_id": user_id}
        headers = {"token": token}
        url = urljoin(self.url_prefix, "logout")
        r = requests.post(url, headers=headers, json=json)
        return r.status_code
```
此处接受user_id, 和Token向服务器发送POST请求，等待返回状态码。
该请求会被路由到be/view/auth中的logout，并调用逻辑代码中的函数。
```
@bp_auth.route("/logout", methods=["POST"])
def logout():
    user_id: str = request.json.get("user_id")
    token: str = request.headers.get("token")
    u = user.User()
    code, message = u.logout(user_id=user_id, token=token)
    return jsonify({"message": message}), code
```
调用be/model/user中的方法logout：

此处调用 self.check_token(user_id, token) 检查用户的 user_id 和 token 是否有效。如果返回的状态码 code 不等于 200，表示令牌验证失败，直接返回相应的状态码和消息。

创建一个新的终端标识符 terminal，生成一个新的虚假 JWT 令牌 dummy_token，用于替换当前的令牌。使用 self.conn['user'].update_one() 方法更新数据库中该用户的 token 和 terminal 信息，将其设置为新的虚假令牌和终端标识。如果没有找到匹配的用户（即 result.matched_count 为 0），调用 error.error_authorization_fail() 返回授权失败的错误信息。
```
            result = self.conn['user'].update_one({'user_id': user_id}, {'$set': {'token': dummy_token, 'terminal': terminal}})
            if result.matched_count == 0:
                return error.error_authorization_fail()
```
如果在数据库操作过程中发生 MongoDB 相关的错误，捕获异常并返回状态码 528 和错误信息。也有一个通用的异常处理，捕获其他可能的错误，返回状态码 530 和错误信息。

如果登出成功，返回状态码 200 和消息 "ok"。

- #### 用户注销
前端请求发起：
```
    def unregister(self, user_id: str, password: str) -> int:
        """
        注销账号
        :param user_id: 用户id
        :param password: 用户密码
        :return: HTTP状态码
        """
        json = {"user_id": user_id, "password": password}
        url = urljoin(self.url_prefix, "unregister")
        r = requests.post(url, json=json)
        return r.status_code
```
这部分使用user_id和password生成一个POST请求，发送给服务器：
```
@bp_auth.route("/unregister", methods=["POST"])
def unregister():
    user_id = request.json.get("user_id", "")
    password = request.json.get("password", "")
    u = user.User()
    code, message = u.unregister(user_id=user_id, password=password)
    return jsonify({"message": message}), code
```
be/view/auth中的后端接口接受请求，并且调用be/model/user中的方法unregister：

该方法调用 self.check_password(user_id, password) 验证用户的 user_id 和 password，如果返回的状态码 code 不等于 200，表示密码验证失败，直接返回相应的状态码和消息。
```
code, message = self.check_password(user_id, password)
```
使用 self.conn['user'].delete_one({'user_id': user_id}) 从数据库中删除对应 user_id 的用户记录。
```
result = self.conn['user'].delete_one({'user_id': user_id})
```
如果 result.deleted_count 不等于 1，表示未成功删除任何记录，调用 error.error_authorization_fail() 返回授权失败的错误信息。如果在数据库操作过程中发生 MongoDB 相关的错误，捕获异常并返回状态码 528 和错误信息。也有一个通用的异常处理，捕获其他可能的错误，返回状态码 530 和错误信息。
如果注销成功，返回状态码 200 和消息 "ok"。

- #### 修改密码
前端请求发起：
```
    def password(self, user_id: str, old_password: str, new_password: str) -> int:
        """
        修改密码
        :param user_id: 接受的用户id
        :param old_password: 接受的旧用户密码
        :param new_password: 接受的新用户密码
        :return: HTTP状态码
        """
        json = {
            "user_id": user_id,
            "oldPassword": old_password,
            "newPassword": new_password,
        }
        url = urljoin(self.url_prefix, "password")
        r = requests.post(url, json=json)
        return r.status_code
```
接收user_id和old_password以及new_password，向服务器发送POST请求，be/view/auth中的后端接口处理请求：
```
@bp_auth.route("/password", methods=["POST"])
def change_password():
    user_id = request.json.get("user_id", "")
    old_password = request.json.get("oldPassword", "")
    new_password = request.json.get("newPassword", "")
    u = user.User()
    code, message = u.change_password(
        user_id=user_id, old_password=old_password, new_password=new_password
    )
    return jsonify({"message": message}), code
```
调用be/model/user中的change_password：

此方法先调用 self.check_password(user_id, old_password) 验证用户的 user_id 和 old_password。如果返回的状态码 code 不等于 200，表示旧密码验证失败，直接返回相应的状态码和消息。

创建一个新的终端标识符 terminal，使用 jwt_encode(user_id, terminal) 生成新的 JWT 令牌，并将其存储在变量 token 中

使用 self.conn['user'].update_one() 方法更新数据库中该用户的记录，将 password 更新为 new_password，同时更新 token 和 terminal。

如果在数据库操作过程中发生 MongoDB 相关的错误，捕获异常并返回状态码 528 和错误信息。也有一个通用的异常处理，捕获其他可能的错误，返回状态码 530 和错误信息。如果修改密码成功，返回状态码 200 和消息 "ok"。

关键更新代码：
```
            self.conn['user'].update_one(
                {'user_id': user_id},
                {'$set': {
                    'password': new_password,
                    'token': token,
                    'terminal': terminal,
                }},
            )"
```

#### 买家权限接口：
这部分的实现逻辑与前面的用户权限没有什么区别，关键点依旧在于修改逻辑代码中的有关数据库的操作。
前端买家类：
初始化：
```
"""
        url_prefix:基础 URL，用于构建请求的完整 URL
        user_id:买家的用户 ID
        password:买家的密码
        self.token: 初始化时为空，会通过登录获取
        self.terminal: 终端信息，用于标识请求来源。
        """
        self.url_prefix = urljoin(url_prefix, "buyer/")
        self.user_id = user_id
        self.password = password
        self.token = ""
        self.terminal = "my terminal"
```
上面这部分实现登录操作：创建 Auth 对象以处理身份验证，调用 login 方法进行登录，并获取状态码和令牌，使用 assert 确保登录成功:
```
self.auth = Auth(url_prefix)
        code, self.token = self.auth.login(self.user_id, self.password, self.terminal)
        assert code == 200
```

- #### 创建新订单
前端发起请求：
```
json = {"user_id": self.user_id, "store_id": store_id, "books": books}
```

store_id和书籍ID与数量的元组向服务器发送POST请求，be/view/buyer中的后端接口new_order()处理请求。
创建实例并调用be/model/buyer中的new_order：

这个方法先检查用户 ID 和商店 ID 是否存在：如果不存在，返回相应错误信息。

使用 UUID 生成一个唯一的订单 ID。

创建一个包含订单基本信息的字典（order）。处理每个图书的订单详情：遍历 id_and_count，检查每本书的库存：如果书籍不存在，返回相应错误信息；如果库存不足，返回相应错误信息。
```
result = self.conn["store"].update_one(
                    {"store_id": store_id, "book_id": book_id, "stock_level": {"$gte": count}},
                    {"$inc": {"stock_level": -count}}
                )
```
```
book_info = json.loads(book["book_info"])
                price = book_info.get("price")
                order_detail = {
                    "order_id": uid,
                    "book_id": book_id,
                    "count": count,
                    "price": price
                }
                order_details.append(order_detail)
```
然后更新库存。将订单详情（如书籍 ID、数量、价格等）添加到 order_details 列表中。
```
if order_details:
    self.conn["new_order_detail"].insert_many(order_details)
    self.conn["new_order"].insert_one(order)
    order_id = uid
```
将订单和订单详情插入数据库的相应集合中。
##### ！！此代码实现部分新功能：历史订单和订单自动取消功能
启动一个定时器，30 秒后自动调用 cancel_order 方法取消该订单
```
timer = threading.Timer(30.0, self.cancel_order, args=[user_id, order_id])
timer.start()  # 延迟队列
```
设置订单状态为 "pending"(已支付)，并将其插入历史订单集合。启动一个定时器，30 秒后自动调用 cancel_order 方法取消该订单。这部分用于实现后面要求中的买家下单后，经过一段时间超时仍未付款，订单也会自动取消。
```
order["status"] = "pending"
self.conn["history_order"].insert_one(order)
self.conn["history_order_detail"].insert_many(order_details)
```
错误捕获：捕获数据库相关的错误和其他异常，并记录错误信息。如果一切顺利，返回状态码 200 和订单 ID。


- #### 支付订单
前端发起请求：
```
json = {
            "user_id": self.user_id,
            "password": self.password,
            "order_id": order_id,
        }
```
在请求体中包含订单号和状态码向服务器发送POST请求，be/view/buyer中的后端接口payment()处理请求。

此接口会调用be/model/buyer中的payment方法用于支付：

payment 方法：

先进行参数验证，通过订单 ID 查询订单。如果找不到订单，返回无效订单 ID 的错误。验证用户 ID 是否与订单的用户 ID 匹配。如果不匹配，返回授权失败的错误。

再进行用户验证，查询买家的信息，包括余额和密码。如果买家不存在，返回相应错误。验证提供的密码是否正确。如果不正确，返回授权失败的错误。

还需要验证店铺信息，查询商店信息。如果找不到商店，返回相应错误。获取商店的卖家 ID，并验证该 ID 是否存在。

查询与该订单关联的所有订单详情，计算订单的总价格。检查买家的余额是否足够支付总金额。如果余额不足，返回资金不足的错误。

检查完以上便可以执行交易，更新买家的余额，扣除订单的总金额，更新卖家的余额，增加订单的总金额。
```
 result = conn["user"].update_one(
                {"user_id": buyer_id, "balance": {"$gte": total_price}},
                {"$inc": {"balance": -total_price}}
            )
```
删除 new_order 和 new_order_detail 中的相关记录，以清理已支付的订单。
```
result = conn["new_order"].delete_one({"order_id": order_id})
```
```
result = conn["new_order_detail"].delete_many({"order_id": order_id})
```
还需要更新历史订单，便于新功能加入。
```
result = conn["history_order"].update_one(
    {"order_id": order_id},
    {"$set": {"status": "paid"}}
)
```
如果没有异常，支付成功，返回状态码 200 和 "ok"。

- #### 账户充值
前端发起请求：
```
json = {
            "user_id": self.user_id,
            "password": self.password,
            "add_value": add_value,
        }
```
构造请求体包括充值金额向服务器发送POST请求，be/view/buyer中的后端接口add_funds()处理请求。

调用be/model/buyer中的add_funds方法：

此方法先进行用户验证：根据用户 ID 从数据库中查询用户信息。如果用户不存在，返回授权失败的错误。验证输入的密码是否与存储的密码匹配。如果不匹配，返回授权失败的错误。

然后使用update_one 方法增加用户的余额。这里使用 $inc 操作符来增加指定的 add_value：
```
result = self.conn["user"].update_one(
                {"user_id": user_id},
                {"$inc": {"balance": add_value}}
            )
```
检查修改计数（modified_count）以确保更新成功。如果没有用户记录被修改，返回用户不存在的错误。

捕获与数据库相关的错误，返回错误代码和消息。捕获其他异常，返回通用错误代码和消息。如果操作成功，返回状态码 200 和 "ok"。

#### 卖家权限接口：
这部分的实现逻辑与前面的两个权限功能的实现没有什么区别，关键点依旧在于修改逻辑代码中的有关数据库的操作。
前端卖家类：
```
class Seller:
    def __init__(self, url_prefix, seller_id: str, password: str):
        """
        url_prefix:基础 URL，用于构建请求的完整 URL
        user_id:卖家的用户 ID
        password:卖家的密码
        self.token: 初始化时为空，会通过登录获取
        self.terminal: 终端信息，用于标识请求来源。
        """
        self.url_prefix = urljoin(url_prefix, "seller/")
        self.seller_id = seller_id
        self.password = password
        self.terminal = "my terminal"
        """
        这部分实现登录操作
        创建 Auth 对象以处理身份验证
        调用 login 方法进行登录，并获取状态码和令牌
        使用 assert 确保登录成功
        """
        self.auth = Auth(url_prefix)
        code, self.token = self.auth.login(self.seller_id, self.password, self.terminal)
        assert code == 200
```
这部分基本上与前面的买家类的实现一致。初始化需要对Auth对象身份验证，确认是已经注册的用户。

- #### 新建店铺
前端请求生成：
```
json = {
            "user_id": self.seller_id,
            "store_id": store_id,
        }
```
请求体包括seller_id和store_id向服务器发送POST请求，be/view/seller中的后端接口seller_create_store处理请求。

调用be/model/seller中的create_store方法：

 此方法用于为用户创建一个新的商店：

 先检查提供的 user_id 是否存在。如果不存在，返回用户不存在的错误。其次检查提供的 store_id 是否已存在。如果存在，返回商店已存在的错误。

 然后就可以创造商店文档：构建一个包含 store_id 和 user_id 的文档 (user_store_doc)。使用 insert_one 方法将新商店文档插入到 user_store 集合中。

```
 user_store_doc = {
                'store_id': store_id,
                'user_id': user_id,
            }
            self.conn['user_store'].insert_one(user_store_doc)
```

如果操作成功，返回状态码 200 和 "ok"。


- #### 加书
前端请求生成：
```
json = {
            "user_id": self.seller_id,
            "store_id": store_id,
            "book_info": book_info.__dict__,
            "stock_level": stock_level,
        }
```
请求体包括用户ID，店铺ID，书籍信息和库存，向服务器发送POST请求，be/view/seller中的后端接口seller_add_book处理请求。

路由调用be/model/seller中的add_book方法。

该方法用于在指定商店中添加一本书：

首先进行用户验证和商店验证：检查提供的 user_id 是否存在。如果不存在，返回用户不存在的错误；检查提供的 store_id 是否存在。如果不存在，返回商店不存在的错误。

同时，也需要进行书籍检查：查在指定商店中是否已经存在相同的 book_id。如果存在，返回书籍已存在的错误。

随后我们就可以准备插入：

构建一个包含书籍信息的文档 (book_doc)，包括商店 ID、书籍 ID、书籍信息（JSON 字符串）和库存水平。
使用 insert_one 方法将新书籍文档插入到 store 集合中。

```
 book_doc = {
                'store_id': store_id,
                'book_id': book_id,
                'book_info': book_json_str,
                'stock_level': stock_level,
            }
            self.conn['store'].insert_one(book_doc)
```

如果操作成功，返回状态码 200 和 "ok"。
- #### 加书籍库存
前端请求生成：
```
json = {
            "user_id": seller_id,
            "store_id": store_id,
            "book_id": book_id,
            "add_stock_level": add_stock_num,
        }
```
请求体中包括用户ID，店铺ID，书籍ID和只增加的库存，向服务器发送POST请求，be/view/seller中的后端接口处理请求。

调用be/model/seller中的add_stock_level方法：

add_stock_level 方法，用于增加指定书籍的库存量：

首先进行用户验证和商店验证：检查提供的 user_id 是否存在。如果不存在，返回用户不存在的错误；检查提供的 store_id 是否存在。如果不存在，返回商店不存在的错误。

使用 self.book_id_exist(store_id, book_id) 检查在指定商店中是否存在相应的书籍。如果不存在，返回书籍不存在的错误。

使用 update_one 方法更新数据库中指定书籍的库存，增加 add_stock_level 的数量。这里使用 $inc 操作符来实现增量更新：
```
self.conn['store'].update_one(
        {'store_id': store_id, 'book_id': book_id},
        {'$inc': {'stock_level': add_stock_level}},
    )
```
如果操作成功，返回状态码 200 和 "ok"。

以上便是前百分之六十内容的全部实现。
#### 前60%功能的代码测试
前60%代码测试的部分调用前端发起请求，与基于的数据库无关，没有增加新功能，因此保持不变，我们直接使用即可。
### 后40%功能的实现
#### 新功能的实现
- 加入新的错误码和错误处理函数

- 加入新的前后端接口

- 加入新的后端逻辑代码

- 新的文档集合
依照前60%的功能，新增两个文档集合：history_order和history_order_detail

- 新增订单状态，有五四种订单状态，分别是：已下单未付款，已付款未发货，已发货未收货，确认收货，订单取消。订单付款后进入history_order文档集合，后面要根据买家和买家的行为调整更新订单状态。


- 编写对每个功能编写新的测试代码



#### 用户权限接口
- #### 搜索书籍
前端请求生成：
```
json = {"title": title, "content": content, "tag": tag, "store_id": store_id}
```
请求体中包括用户ID，店铺ID，书籍ID和只增加的库存，向服务器发送POST请求，be/view/auth中的后端接口处理请求。
调用be/model/user中的search_book方法：
创建一个空字典 query，用于构建 MongoDB 查询条件。根据提供的参数（title、content、tag）动态添加查询条件。使用 regex 进行模糊匹配：
如果提供了 title，则在查询中添加 "title": {"regex": title}。
如果提供了 content，则在查询中添加 "content": {"regex": content}。
如果提供了 tag，则在查询中添加 "tags": {"regex": tag}。
```
query = {}
    if title:
        query['title'] = {"$regex": title}
    if content:
        query['content'] = {"$regex": content}
    if tag:
        query['tags'] = {"$regex": tag}
```
查询前需要先检查 store_id 是否为空，如果不为空，查询 store 集合，获取该商店下的所有书籍 ID。如果没有找到相应的商店，返回商店不存在的错误。从查询结果中提取所有书籍 ID，并将其添加到查询条件中，使用 $in 来匹配。如果为空，则进行全站查询。

使用构建的 query 在 books 集合中查找匹配的书籍，并将结果转换为列表。
```
results = list(self.conn["books"].find(query))
```
如果没有找到匹配的书籍，返回状态码 529 和相关消息。

如果找到匹配的书籍，返回状态码 200 和 "ok"。
- #### 测试代码（搜索图书）
测试代码测试书籍搜索功能的不同场景。

TestSearchBook：一个包含多个测试用例的类，专门用于测试书籍搜索功能。

test_search_global 方法：
测试不同条件下的搜索功能，验证能否找到存在的书籍。使用书籍的标题、内容、标签进行单独和组合搜索，确保返回状态码为 200（成功）。

test_search_global_not_exists 方法：
测试使用不存在的标题、内容和标签进行搜索，验证返回状态码为 529

test_search_in_store 方法：
测试在特定商店中搜索书籍，验证使用商店中的书籍的标题、内容和标签进行搜索时，返回状态码为 200。

test_search_not_exist_store_id 方法：
测试使用不存在的商店 ID 进行搜索，验证返回状态码为 513（商店不存在）。

test_search_in_store_not_exist 方法：
测试在指定商店中搜索不存在的书籍，验证返回状态码为 529。

通过断言来确保返回的状态码符合预期。

#### 卖家权限接口
- #### 发货
前端请求生成：
```
json = {
            "user_id": self.seller_id,
            "store_id": store_id,
            "order_id": order_id,
        }
```
请求体中包括用户ID，店铺ID和订单号，向服务器发送POST请求，be/view/seller中的后端send_order接口处理请求。
调用be/model/seller中的send_order方法：
首先进行用户验证和商店验证：
使用 self.user_id_exist(user_id) 检查提供的用户 ID 是否存在。如果不存在，返回用户不存在的错误。使用 self.store_id_exist(store_id) 检查提供的商店 ID 是否存在。如果不存在，返回商店不存在的错误。
其次进行订单查找，在 history_order 集合中查找指定的订单 ID。如果未找到相应的订单，返回无效订单 ID 的错误。
```
if not order:
     return error.error_invalid_order_id(order_id)
```
接着要检查订单状态：检查订单的状态是否为 'paid'。如果不是，返回未付款的错误。
```
 if status != 'paid':
                return error.error_not_paid(order_id)
```
最后，使用 update_one 方法更新订单的状态，将其设置为 'sent'，表示订单已发货。
```
self.conn['history_order'].update_one(
                {'order_id': order_id},
                {'$set': {'status': 'sent'}},
            )
```
如果操作成功，返回状态码 200 和 "ok"。


#### 买家权限接口
- #### 获取历史订单
前端请求生成：
```
json = {
            "user_id": self.user_id,
    }
```
请求体中包括用户ID，向服务器发送POST请求，be/view/buyer中的后端get_history_order接口处理请求。
调用be/model/buyer中的get_history_order方法：
使用 user_id 从数据库中查询与该用户相关的历史订单。调用 self.conn["history_order"].find({"user_id": user_id})。
```
 orders = self.conn["history_order"].find({"user_id": user_id})
```
将查询结果转换为列表 orders_list。如果没有找到订单，返回状态码和错误信息，并且返回一个空列表。
初始化一个空列表 order_list 来存储每个订单的详细信息。遍历 orders_list 中的每个订单：
先获取订单 ID。再根据订单 ID 查询该订单的所有详细信息，使用 self.conn["history_order_detail"].find({"order_id": order_id})。
初始化一个空列表 order_detail_list 来存储该订单的书籍详情。
遍历订单的详细信息，提取 book_id、count 和 price，并构建字典 order_detail，然后将其添加到 order_detail_list。
```
 for detail in order_details:
    book_id = detail["book_id"]
    count = detail["count"]
    price = detail["price"]
    order_detail = {
        "book_id": book_id,
        "count": count,
        "price": price
    }
    order_detail_list.append(order_detail)
```
创建一个字典 order_info，包含 order_id 和 order_detail_list，并将其添加到 order_list，返回结构化的结果。
```
order_info = {
                    "order_id": order_id,
                    "order_detail": order_detail_list
                }
                order_list.append(order_info)
```
如果没有异常，返回状态码 200、消息 "ok" 和构建好的 order_list。
- #### 测试代码（获取历史订单）
test_ok:测试正常情况下获取订单历史的功能。调用 get_history_order 方法，检查返回状态码是否为 200。

test_non_exist_user_id:测试使用不存在的用户 ID 获取订单历史。期望返回的状态码不是 200。

- #### 取消订单
前端请求生成：
```
json = {
            "user_id": self.user_id,
            "order_id": order_id,
        }
```
请求体中包括用户ID和订单号，向服务器发送POST请求，be/view/buyer中的后端cancel_order接口处理请求。
调用be/model/buyer中的cancel_order方法：
使用 self.conn["new_order"].find_one({"order_id": order_id}) 从数据库中查询订单。如果未找到该订单，则返回相应的错误信息（error.error_invalid_order_id(order_id)）。
```
order = self.conn["new_order"].find_one({"order_id": order_id})
```
从订单中获取 buyer_id。检查 buyer_id 是否与传入的 user_id 匹配。如果不匹配，则返回授权失败的错误信息（error.error_authorization_fail()）
调用 self.conn["new_order"].delete_one({"order_id": order_id}) 删除订单。如果删除的计数为 0，表示订单未找到，再次返回错误信息（error.error_invalid_order_id(order_id)）。使用 self.conn["new_order_detail"].delete_many({"order_id": order_id}) 删除与该订单相关的所有详情。如果删除的计数为 0，再次返回错误信息。
```
result = self.conn["new_order"].delete_one({"order_id": order_id})
```
```
self.conn["new_order_detail"].delete_many({"order_id": order_id})
```
调用 self.conn["history_order"].update_one() 更新该订单的状态为 "cancelled"。如果更新的计数为 0，表示订单未找到，返回错误信息。
```
 result = self.conn["history_order"].update_one(
    {"order_id": order_id},
    {"$set": {"status": "cancelled"}}
)
```
如果所有步骤成功完成，返回状态码 200 和字符串 "ok"，表示订单取消成功。
- #### 测试代码（取消订单）
test_ok:测试取消成功的情况。

test_non_exist_order_id:测试尝试取消一个不存在的订单 ID。添加 "_x" 后缀来模拟不存在的订单.

test_repeat_cancel:测试重复取消同一订单的情况。

test_cancel_paid_order:测试尝试取消已付款的订单。

test_cancel_long_time_order:测试取消一个超时的订单。通过 time.sleep(31) 模拟订单超时。

- #### 确认收货
前端请求生成：
```
json = {
            "user_id": self.user_id,
            "order_id": order_id,
        }
```
请求体中包括用户ID和订单号，向服务器发送POST请求，be/view/buyer中的后端receive_order接口处理请求。

调用be/model/buyer中的receive_order方法：

使用 self.conn["history_order"].find_one({"order_id": order_id}) 从数据库中查找指定的订单。如果未找到该订单，返回相应的错误信息（error.error_invalid_order_id(order_id)）。
```
 order = self.conn["history_order"].find_one({"order_id": order_id})
```
还是要验证用户身份，从订单中获取 buyer_id，检查其是否与传入的 user_id 匹配。如果不匹配，返回授权失败的错误信息（error.error_authorization_fail()）。
同时也要检查订单状态，获取订单的状态，如果状态不是 "sent"，则返回相应的错误信息（error.error_not_sent(order_id)）。
最后调用 self.conn["history_order"].update_one() 方法，将订单状态更新为 "received"。如果更新的计数为 0，表示订单未找到，返回错误信息（error.error_invalid_order_id(order_id)）。
```
 result = self.conn["history_order"].update_one(
                {"order_id": order_id},
                {"$set": {"status": "received"}}
            )
```
如果所有步骤成功完成，返回状态码 200 和字符串 "ok"，表示订单接收成功。
- #### 测试代码（收货发货）
测试了订单发送和接收功能，确保覆盖了各种条件和边缘情况。每个测试方法都包含断言以验证预期结果，从而验证功能的完备性。

test_send_ok：测试卖家是否可以成功发送订单。

test_receive_ok：测试卖家发送订单后，买家能否成功接收该订单。

test_error_store_id：测试发送订单时使用无效的商店 ID。

test_error_order_id：测试发送订单时使用无效的订单 ID。

test_error_seller_id：修改卖家 ID 为无效值，并测试发送订单。

test_error_buyer_id：发送订单后，修改买家 ID 为无效值，测试买家接收订单。

test_send_not_pay：测试未支付的订单是否可以发送。

test_receive_not_send：测试买家尝试接收未发送的订单。

test_repeat_send：测试卖家是否可以多次发送同一订单。

test_repeat_receive：测试买家是否可以多次接收同一订单。


### 实验测试执行结果
运行以下命令执行项目测试：

    $ bash script/test.sh

测试结果如下：
```
liwanting@LWT MINGW64 /c/school/pythonprojects/bookstore_sql/project1/bookstore (master)
$ bash script/test.sh
============================= test session starts =============================
platform win32 -- Python 3.11.5, pytest-8.3.3, pluggy-1.5.0 -- C:\school\python\python.exe
cachedir: .pytest_cache
rootdir: C:\school\pythonprojects\bookstore_sql\project1\bookstore
collecting ... frontend begin test
 * Serving Flask app 'be.serve' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
2024-12-26 23:21:49,658 [Thread-1 (ru] [INFO ]   * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
collected 54 items

fe/test/test_add_book.py::TestAddBook::test_ok PASSED                    [  1%]
fe/test/test_add_book.py::TestAddBook::test_error_non_exist_store_id PASSED [  3%]
fe/test/test_add_book.py::TestAddBook::test_error_exist_book_id PASSED   [  5%]
fe/test/test_add_book.py::TestAddBook::test_error_non_exist_user_id PASSED [  7%]
fe/test/test_add_funds.py::TestAddFunds::test_ok PASSED                  [  9%]
fe/test/test_add_funds.py::TestAddFunds::test_error_user_id PASSED       [ 11%]
fe/test/test_add_funds.py::TestAddFunds::test_error_password PASSED      [ 12%]
fe/test/test_add_stock_level.py::TestAddStockLevel::test_error_user_id PASSED [ 14%]
fe/test/test_add_stock_level.py::TestAddStockLevel::test_error_store_id PASSED [ 16%]
fe/test/test_add_stock_level.py::TestAddStockLevel::test_error_book_id PASSED [ 18%]
fe/test/test_add_stock_level.py::TestAddStockLevel::test_ok PASSED       [ 20%]
fe/test/test_cancel_order.py::TestCancelOrder::test_ok PASSED            [ 22%]
fe/test/test_cancel_order.py::TestCancelOrder::test_non_exist_order_id PASSED [ 24%]
fe/test/test_cancel_order.py::TestCancelOrder::test_repeat_cancel PASSED [ 25%]
fe/test/test_cancel_order.py::TestCancelOrder::test_cancel_paid_order PASSED [ 27%]
fe/test/test_cancel_order.py::TestCancelOrder::test_cancel_long_time_order PASSED [ 29%]
fe/test/test_create_store.py::TestCreateStore::test_ok PASSED            [ 31%]
fe/test/test_create_store.py::TestCreateStore::test_error_exist_store_id PASSED [ 33%]
fe/test/test_get_history_order.py::TestGetOHistoryaoarder::test_ok PASSED [ 35%]
fe/test/test_get_history_order.py::TestGetOHistoryaoarder::test_non_exist_user_id PASSED [ 37%]
fe/test/test_login.py::TestLogin::test_ok PASSED                         [ 38%]
fe/test/test_login.py::TestLogin::test_error_user_id PASSED              [ 40%]
fe/test/test_login.py::TestLogin::test_error_password PASSED             [ 42%]
fe/test/test_new_order.py::TestNewOrder::test_non_exist_book_id PASSED   [ 44%]
fe/test/test_new_order.py::TestNewOrder::test_low_stock_level PASSED     [ 46%]
fe/test/test_new_order.py::TestNewOrder::test_ok PASSED                  [ 48%]
fe/test/test_new_order.py::TestNewOrder::test_non_exist_user_id PASSED   [ 50%]
fe/test/test_new_order.py::TestNewOrder::test_non_exist_store_id PASSED  [ 51%]
fe/test/test_password.py::TestPassword::test_ok PASSED                   [ 53%]
fe/test/test_password.py::TestPassword::test_error_password PASSED       [ 55%]
fe/test/test_password.py::TestPassword::test_error_user_id PASSED        [ 57%]
fe/test/test_payment.py::TestPayment::test_ok PASSED                     [ 59%]
fe/test/test_payment.py::TestPayment::test_authorization_error PASSED    [ 61%]
fe/test/test_payment.py::TestPayment::test_not_suff_funds PASSED         [ 62%]
fe/test/test_payment.py::TestPayment::test_repeat_pay PASSED             [ 64%]
fe/test/test_register.py::TestRegister::test_register_ok PASSED          [ 66%]
fe/test/test_register.py::TestRegister::test_unregister_ok PASSED        [ 68%]
fe/test/test_register.py::TestRegister::test_unregister_error_authorization PASSED [ 70%]
fe/test/test_register.py::TestRegister::test_register_error_exist_user_id PASSED [ 72%]
fe/test/test_search_book.py::TestSearchBook::test_search_in_store PASSED [ 74%]
fe/test/test_search_book.py::TestSearchBook::test_search_global PASSED   [ 75%]
fe/test/test_search_book.py::TestSearchBook::test_search_global_not_exists PASSED [ 77%]
fe/test/test_search_book.py::TestSearchBook::test_search_not_exist_store_id PASSED [ 79%]
fe/test/test_search_book.py::TestSearchBook::test_search_not_in_store SKIPPED [ 81%]
fe/test/test_send_order.py::TestSendReceive::test_send_ok PASSED         [ 83%]
fe/test/test_send_order.py::TestSendReceive::test_receive_ok PASSED      [ 85%]
fe/test/test_send_order.py::TestSendReceive::test_error_store_id PASSED  [ 87%]
fe/test/test_send_order.py::TestSendReceive::test_error_order_id PASSED  [ 88%]
fe/test/test_send_order.py::TestSendReceive::test_error_seller_id PASSED [ 90%]
fe/test/test_send_order.py::TestSendReceive::test_error_buyer_id PASSED  [ 92%]
fe/test/test_send_order.py::TestSendReceive::test_send_not_pay PASSED    [ 94%]
fe/test/test_send_order.py::TestSendReceive::test_receive_not_send PASSED [ 96%]
fe/test/test_send_order.py::TestSendReceive::test_repeat_send PASSED     [ 98%]
fe/test/test_send_order.py::TestSendReceive::test_repeat_receive PASSED  [100%]C:\school\pythonprojects\bookstore_sql\project1\bookstore\be\serve.py:18: UserWarning: The 'environ['werkzeug.server.shutdown']' function is deprecated and will be removed in Werkzeug 2.1.
  func()
2024-12-26 23:23:25,628 [Thread-649 (] [INFO ]  127.0.0.1 - - [26/Dec/2024 23:23:25] "GET /shutdown HTTP/1.1" 200 -


================== 53 passed, 1 skipped in 96.92s (0:01:36) ===================
frontend end test
No data to combine
Name                                Stmts   Miss Branch BrPart  Cover
---------------------------------------------------------------------
be\__init__.py                          0      0      0      0   100%
be\app.py                               3      3      2      0     0%
be\model\buyer.py                     204     40     62     14    80%
be\model\db_conn.py                    21      0      0      0   100%
be\model\error.py                      28      2      0      0    93%
be\model\seller.py                    108     27     38      6    76%
be\model\store.py                      48      5      0      0    90%
be\model\user.py                      205     52     52      9    76%
be\serve.py                            36      1      2      1    95%
be\view\__init__.py                     0      0      0      0   100%
be\view\auth.py                        51      7      0      0    86%
be\view\buyer.py                       54      0      2      0   100%
be\view\seller.py                      39      0      0      0   100%
fe\__init__.py                          0      0      0      0   100%
fe\access\__init__.py                   0      0      0      0   100%
fe\access\auth.py                      36      4      0      0    89%
fe\access\book.py                      69      4     14      2    88%
fe\access\buyer.py                     56      0      2      0   100%
fe\access\new_buyer.py                  8      0      0      0   100%
fe\access\new_seller.py                 8      0      0      0   100%
fe\access\seller.py                    39      0      0      0   100%
fe\bench\__init__.py                    0      0      0      0   100%
fe\bench\run.py                        13     13      6      0     0%
fe\bench\session.py                    47     47     12      0     0%
fe\bench\workload.py                  125    125     20      0     0%
fe\conf.py                             11      0      0      0   100%
fe\conftest.py                         19      0      0      0   100%
fe\test\gen_book_data.py               49      1     16      1    97%
fe\test\test_add_book.py               37      0     10      0   100%
fe\test\test_add_funds.py              23      0      0      0   100%
fe\test\test_add_stock_level.py        40      0     10      0   100%
fe\test\test_cancel_order.py           63      1      8      1    97%
fe\test\test_create_store.py           20      0      0      0   100%
fe\test\test_get_history_order.py      51      1      8      1    97%
fe\test\test_login.py                  28      0      0      0   100%
fe\test\test_new_order.py              40      0      0      0   100%
fe\test\test_password.py               33      0      0      0   100%
fe\test\test_payment.py                60      1      4      1    97%
fe\test\test_register.py               31      0      0      0   100%
fe\test\test_search_book.py            85      6      6      2    91%
fe\test\test_send_order.py             89      1      8      1    98%
---------------------------------------------------------------------
TOTAL                                1877    341    282     39    80%
Wrote HTML report to htmlcov\index.html

liwanting@LWT MINGW64 /c/school/pythonprojects/bookstore_sql/project1/bookstore (master)
$

```
可见项目bookstore中的所有功能均已全部实现:-)

但是test_bench测试如果和它们放在一起没办法通过，在测试完tesr_bench后面的内容均无法测试了不知道为啥，但是test_bench自己可以通过，我找了很久但是没来得及找到原因TT

然后发现把test_bench放到最后就可以一口气过掉，但是会有warning：
```angular2html
liwanting@LWT MINGW64 /c/school/pythonprojects/bookstore_sql/project1/bookstore (master)
$ bash script/test.sh
============================= test session starts =============================
platform win32 -- Python 3.11.5, pytest-8.3.3, pluggy-1.5.0 -- C:\school\python\python.exe
cachedir: .pytest_cache
rootdir: C:\school\pythonprojects\bookstore_sql\project1\bookstore
collecting ... frontend begin test
 * Serving Flask app 'be.serve' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
2024-12-27 00:14:35,863 [Thread-1 (ru] [INFO ]   * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
collected 55 items

fe/test/test_add_book.py::TestAddBook::test_ok PASSED                    [  1%]
fe/test/test_add_book.py::TestAddBook::test_error_non_exist_store_id PASSED [  3%]
fe/test/test_add_book.py::TestAddBook::test_error_exist_book_id PASSED   [  5%]
fe/test/test_add_book.py::TestAddBook::test_error_non_exist_user_id PASSED [  7%]
fe/test/test_add_funds.py::TestAddFunds::test_ok PASSED                  [  9%]
fe/test/test_add_funds.py::TestAddFunds::test_error_user_id PASSED       [ 10%]
fe/test/test_add_funds.py::TestAddFunds::test_error_password PASSED      [ 12%]
fe/test/test_add_stock_level.py::TestAddStockLevel::test_error_user_id PASSED [ 14%]
fe/test/test_add_stock_level.py::TestAddStockLevel::test_error_store_id PASSED [ 16%]
fe/test/test_add_stock_level.py::TestAddStockLevel::test_error_book_id PASSED [ 18%]
fe/test/test_add_stock_level.py::TestAddStockLevel::test_ok PASSED       [ 20%]
fe/test/test_cancel_order.py::TestCancelOrder::test_ok PASSED            [ 21%]
fe/test/test_cancel_order.py::TestCancelOrder::test_non_exist_order_id PASSED [ 23%]
fe/test/test_cancel_order.py::TestCancelOrder::test_repeat_cancel PASSED [ 25%]
fe/test/test_cancel_order.py::TestCancelOrder::test_cancel_paid_order PASSED [ 27%]
fe/test/test_cancel_order.py::TestCancelOrder::test_cancel_long_time_order PASSED [ 29%]
fe/test/test_create_store.py::TestCreateStore::test_ok PASSED            [ 30%]
fe/test/test_create_store.py::TestCreateStore::test_error_exist_store_id PASSED [ 32%]
fe/test/test_get_history_order.py::TestGetOHistoryaoarder::test_ok PASSED [ 34%]
fe/test/test_get_history_order.py::TestGetOHistoryaoarder::test_non_exist_user_id PASSED [ 36%]
fe/test/test_login.py::TestLogin::test_ok PASSED                         [ 38%]
fe/test/test_login.py::TestLogin::test_error_user_id PASSED              [ 40%]
fe/test/test_login.py::TestLogin::test_error_password PASSED             [ 41%]
fe/test/test_new_order.py::TestNewOrder::test_non_exist_book_id PASSED   [ 43%]
fe/test/test_new_order.py::TestNewOrder::test_low_stock_level PASSED     [ 45%]
fe/test/test_new_order.py::TestNewOrder::test_ok PASSED                  [ 47%]
fe/test/test_new_order.py::TestNewOrder::test_non_exist_user_id PASSED   [ 49%]
fe/test/test_new_order.py::TestNewOrder::test_non_exist_store_id PASSED  [ 50%]
fe/test/test_password.py::TestPassword::test_ok PASSED                   [ 52%]
fe/test/test_password.py::TestPassword::test_error_password PASSED       [ 54%]
fe/test/test_password.py::TestPassword::test_error_user_id PASSED        [ 56%]
fe/test/test_payment.py::TestPayment::test_ok PASSED                     [ 58%]
fe/test/test_payment.py::TestPayment::test_authorization_error PASSED    [ 60%]
fe/test/test_payment.py::TestPayment::test_not_suff_funds PASSED         [ 61%]
fe/test/test_payment.py::TestPayment::test_repeat_pay PASSED             [ 63%]
fe/test/test_register.py::TestRegister::test_register_ok PASSED          [ 65%]
fe/test/test_register.py::TestRegister::test_unregister_ok PASSED        [ 67%]
fe/test/test_register.py::TestRegister::test_unregister_error_authorization PASSED [ 69%]
fe/test/test_register.py::TestRegister::test_register_error_exist_user_id PASSED [ 70%]
fe/test/test_search_book.py::TestSearchBook::test_search_in_store PASSED [ 72%]
fe/test/test_search_book.py::TestSearchBook::test_search_global PASSED   [ 74%]
fe/test/test_search_book.py::TestSearchBook::test_search_global_not_exists PASSED [ 76%]
fe/test/test_search_book.py::TestSearchBook::test_search_not_exist_store_id PASSED [ 78%]
fe/test/test_search_book.py::TestSearchBook::test_search_not_in_store SKIPPED [ 80%]
fe/test/test_send_order.py::TestSendReceive::test_send_ok PASSED         [ 81%]
fe/test/test_send_order.py::TestSendReceive::test_receive_ok PASSED      [ 83%]
fe/test/test_send_order.py::TestSendReceive::test_error_store_id PASSED  [ 85%]
fe/test/test_send_order.py::TestSendReceive::test_error_order_id PASSED  [ 87%]
fe/test/test_send_order.py::TestSendReceive::test_error_seller_id PASSED [ 89%]
fe/test/test_send_order.py::TestSendReceive::test_error_buyer_id PASSED  [ 90%]
fe/test/test_send_order.py::TestSendReceive::test_send_not_pay PASSED    [ 92%]
fe/test/test_send_order.py::TestSendReceive::test_receive_not_send PASSED [ 94%]
fe/test/test_send_order.py::TestSendReceive::test_repeat_send PASSED     [ 96%]
fe/test/test_send_order.py::TestSendReceive::test_repeat_receive PASSED  [ 98%]
fe/test/test_z_bench.py::test_bench PASSED                               [100%]C:\school\pythonprojects\bookstore_sql\project1\bookstore\be\serve.py:18: UserWarning: The 'environ['werkzeug.server.shutdown']' function is deprecated and will be removed in Werkzeug 2.1.
  func()
2024-12-27 00:19:00,293 [Thread-2375 ] [INFO ]  127.0.0.1 - - [27/Dec/2024 00:19:00] "GET /shutdown HTTP/1.1" 200 -


============================== warnings summary ===============================
fe/test/test_z_bench.py::test_bench
  C:\school\python\Lib\site-packages\_pytest\threadexception.py:82: PytestUnhandledThreadExceptionWarning: Exception in thread Thread-1277

  Traceback (most recent call last):
    File "C:\school\python\Lib\site-packages\requests\models.py", line 974, in json
      return complexjson.loads(self.text, **kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    File "C:\school\python\Lib\site-packages\simplejson\__init__.py", line 514, in loads
      return _default_decoder.decode(s)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^
    File "C:\school\python\Lib\site-packages\simplejson\decoder.py", line 386, in decode
      obj, end = self.raw_decode(s)
                 ^^^^^^^^^^^^^^^^^^
    File "C:\school\python\Lib\site-packages\simplejson\decoder.py", line 416, in raw_decode
      return self.scan_once(s, idx=_w(s, idx).end())
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  simplejson.errors.JSONDecodeError: Expecting value: line 1 column 1 (char 0)

  During handling of the above exception, another exception occurred:

  Traceback (most recent call last):
    File "C:\school\python\Lib\threading.py", line 1038, in _bootstrap_inner
      self.run()
    File "C:\school\pythonprojects\bookstore_sql\project1\bookstore\fe\bench\session.py", line 29, in run
      self.run_gut()
    File "C:\school\pythonprojects\bookstore_sql\project1\bookstore\fe\bench\session.py", line 34, in run_gut
      ok, order_id = new_order.run()
                     ^^^^^^^^^^^^^^^
    File "C:\school\pythonprojects\bookstore_sql\project1\bookstore\fe\bench\workload.py", line 19, in run
      code, order_id = self.buyer.new_order(self.store_id, self.book_id_and_count)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    File "C:\school\pythonprojects\bookstore_sql\project1\bookstore\fe\access\buyer.py", line 53, in new_order
      response_json = r.json()
                      ^^^^^^^^
    File "C:\school\python\Lib\site-packages\requests\models.py", line 978, in json
      raise RequestsJSONDecodeError(e.msg, e.doc, e.pos)
  requests.exceptions.JSONDecodeError: Expecting value: line 1 column 1 (char 0)

    warnings.warn(pytest.PytestUnhandledThreadExceptionWarning(msg))

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
============ 54 passed, 1 skipped, 1 warning in 265.37s (0:04:25) =============
frontend end test
No data to combine
Name                                Stmts   Miss Branch BrPart  Cover
---------------------------------------------------------------------
be\__init__.py                          0      0      0      0   100%
be\app.py                               3      3      2      0     0%
be\model\buyer.py                     204     40     62     14    80%
be\model\db_conn.py                    21      0      0      0   100%
be\model\error.py                      28      2      0      0    93%
be\model\seller.py                    108     27     38      6    76%
be\model\store.py                      48      5      0      0    90%
be\model\user.py                      205     52     52      9    76%
be\serve.py                            36      1      2      1    95%
be\view\__init__.py                     0      0      0      0   100%
be\view\auth.py                        51      7      0      0    86%
be\view\buyer.py                       54      0      2      0   100%
be\view\seller.py                      39      0      0      0   100%
fe\__init__.py                          0      0      0      0   100%
fe\access\__init__.py                   0      0      0      0   100%
fe\access\auth.py                      36      4      0      0    89%
fe\access\book.py                      69      0     14      2    98%
fe\access\buyer.py                     56      0      2      0   100%
fe\access\new_buyer.py                  8      0      0      0   100%
fe\access\new_seller.py                 8      0      0      0   100%
fe\access\seller.py                    39      0      0      0   100%
fe\bench\__init__.py                    0      0      0      0   100%
fe\bench\run.py                        13      0      6      0   100%
fe\bench\session.py                    47     10     12      3    71%
fe\bench\workload.py                  125     20     20      2    83%
fe\conf.py                             11      0      0      0   100%
fe\conftest.py                         19      0      0      0   100%
fe\test\gen_book_data.py               49      0     16      0   100%
fe\test\test_add_book.py               37      0     10      0   100%
fe\test\test_add_funds.py              23      0      0      0   100%
fe\test\test_add_stock_level.py        40      0     10      0   100%
fe\test\test_cancel_order.py           63      1      8      1    97%
fe\test\test_create_store.py           20      0      0      0   100%
fe\test\test_get_history_order.py      51      1      8      1    97%
fe\test\test_login.py                  28      0      0      0   100%
fe\test\test_new_order.py              40      0      0      0   100%
fe\test\test_password.py               33      0      0      0   100%
fe\test\test_payment.py                60      1      4      1    97%
fe\test\test_register.py               31      0      0      0   100%
fe\test\test_search_book.py            85      6      6      2    91%
fe\test\test_send_order.py             89      1      8      1    98%
fe\test\test_z_bench.py                 6      2      0      0    67%
---------------------------------------------------------------------
TOTAL                                1883    183    282     43    89%
Wrote HTML report to htmlcov\index.html

liwanting@LWT MINGW64 /c/school/pythonprojects/bookstore_sql/project1/bookstore (master)

```
现在可以看见我的测试都通过了，要求均已经实现，每个功能都写了测试并且测试通过。
有skip是因为不满足那个测试的要求，此测试要求有在books库中但现在别的书店里没有的书，不符合要求的情况下这个测试会skip，因此有一个skip。

## 项目亮点
### 亮点1：使用git进行版本管理
GitHub 使用 Git 作为版本控制系统，能够跟踪代码的历史变化，便于查看和恢复以前的版本，也便于多人协作工作。
#### 代码仓库：
https://github.com/liququ2023/datadase_project1
### 亮点2：测试与覆盖率
此处看见代码覆盖率不高是因为bench相关部分没有运行，其他部分的覆盖率还不错。
## 项目总结
本项目是我们再一次体验构建一个包含这么多功能的后端架构，且包含前端的测试，是一个功能相对完善的项目。在深入理解数据库在项目中与前后端的交互过程的同时，也更多地了解了前后端应用架构的知识，也比较了不同的数据库在应用上的区别。