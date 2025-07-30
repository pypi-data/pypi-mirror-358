import mysql.connector


def 连接数据库(主机, 用户名, 密码, 数据库名, 字符集='utf8mb4'):
    """
    连接到MySQL数据库并返回 连接对象, 游标对象。

    参数：
        - 主机：数据库主机名或IP地址。
        - 用户名：数据库用户名。
        - 密码：数据库密码。
        - 数据库名：要连接的数据库名。
        - 字符集：要使用的字符集（默认值为 'utf8mb4'，可同时兼容'utf8'）。

    返回值：
        - 连接对象：表示与数据库的连接。如果连接失败，则返回 None。
        - 游标对象：用于执行查询和获取结果。如果连接失败，则返回 None。

    使用示例（可以复制并直接修改）：
        连接对象, 游标对象 = 连接数据库("127.0.0.1", "root", "root", "test", 字符集='utf8mb4')

        # 替换参数：
         - 主机：如 "localhost" 或 "127.0.0.1"
         - 用户名：数据库的登录用户名，如 "root"
         - 密码：登录用户的密码，如 "password"
         - 数据库名：需要连接的数据库名称，如 "test_db"
         - 字符集：可以不修改，默认值 'utf8mb4' 兼容 'utf8'
    """
    try:
        # 连接到数据库，设置字符集
        连接对象 = mysql.connector.connect(
            host=主机,
            user=用户名,
            password=密码,
            database=数据库名,
            charset=字符集
        )

        # 创建游标对象
        游标对象 = 连接对象.cursor()

        # 返回连接对象和游标对象
        return 连接对象, 游标对象
    except Exception:
        return None, None