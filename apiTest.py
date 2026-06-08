from flask import Flask, jsonify, request, send_file
from gtts import gTTS
from gtts.tts import gTTSError
import io
from flask_cors import CORS
import pymysql
from pymysql.err import MySQLError

DB_NAME = 'testData'
USER_TABLE_NAME = 'userinfo'

DB_CONFIG = {
    'host': 'localhost',  # 本地主机
    'port': 3306,  # MySQL 默认端口
    'user': 'root',  # 你的数据库用户名
    'password': 'lpf020918',  # 你的数据库密码
    'database': DB_NAME,  # 你刚才创建的数据库名称
    'charset': 'utf8mb4'  # 强烈建议使用 utf8mb4，支持中文和表情符号
}


def ensure_database_exists():
    """连接 MySQL 服务并确保目标数据库存在。"""
    server_config = DB_CONFIG.copy()
    server_config.pop('database')

    with pymysql.connect(**server_config) as conn:
        with conn.cursor() as cursor:
            # 数据库名来自固定常量，不接收用户输入，避免 SQL 注入风险。
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )


def get_db_connection():
    ensure_database_exists()
    return pymysql.connect(**DB_CONFIG)


def ensure_user_table(conn):
    """确保提交接口需要的用户表存在。"""
    with conn.cursor() as cursor:
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS `{USER_TABLE_NAME}` (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(64) NOT NULL,
                phone VARCHAR(64) NOT NULL,
                pwd VARCHAR(128) NOT NULL,
                gz FLOAT(8,2) NOT NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        cursor.execute(f"SHOW COLUMNS FROM `{USER_TABLE_NAME}`")
        existing_columns = {column[0] for column in cursor.fetchall()}

        # 兼容已经按旧字段创建过的本地表，缺哪个字段就补哪个字段。
        if 'name' not in existing_columns:
            cursor.execute(f"ALTER TABLE `{USER_TABLE_NAME}` ADD COLUMN name VARCHAR(64) NULL")
        if 'phone' not in existing_columns:
            cursor.execute(f"ALTER TABLE `{USER_TABLE_NAME}` ADD COLUMN phone VARCHAR(64) NULL")
        if 'user_name' in existing_columns:
            # 旧版本建过 user_name 且设为必填；现在接口不用它，改成可为空避免插入失败。
            cursor.execute(f"ALTER TABLE `{USER_TABLE_NAME}` MODIFY COLUMN user_name VARCHAR(64) NULL")


# 返回数据的工具函数
from utils import api_response

app = Flask(__name__)
CORS(app)


# get请求
@app.route('/api/users', methods=['GET'])
def getUserInfo():
    try:
        with get_db_connection() as conn:
            ensure_user_table(conn)
            # 使用字典游标，这样查出来的数据会带上字段名，方便前端看
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                # 只返回当前接口维护的字段，避免把旧表里的历史字段暴露给前端。
                cursor.execute(f"SELECT id, name, phone, pwd, gz FROM `{USER_TABLE_NAME}`")
                result = cursor.fetchall()  # 获取所有查询结果
        return api_response(message='查询成功', data=result)  # 将数据以 JSON 格式返回给接口调用者
    except MySQLError as e:
        return api_response(code=500, message=f'数据库查询失败：{e}', data=None)


# post 请求
@app.route('/submit', methods=['POST'])
def submitData():
    data = request.get_json(silent=True)
    if not data:
        return api_response(code=400, message='请求失败', data=None)

    # 2. 使用 .get() 方法安全提取字段，如果没有该字段默认为空字符串
    name = str(data.get('name', '')).strip()
    phone = str(data.get('phone', '')).strip()
    pwd = str(data.get('pwd', '')).strip()

    # 3. 进行业务校验
    if not name:
        return api_response(code=400, message='姓名不能为空', data=None)
    if not phone:
        return api_response(code=400, message='手机号不能为空', data=None)
    if not pwd:
        return api_response(code=400, message='密码不能为空', data=None)

    try:
        with get_db_connection() as conn:
            ensure_user_table(conn)
            with conn.cursor() as cursor:
                cursor.execute(f"SHOW COLUMNS FROM `{USER_TABLE_NAME}`")
                existing_columns = {column[0] for column in cursor.fetchall()}

                insert_columns = ['name', 'phone', 'pwd']
                insert_values = [name, phone, pwd]

                column_sql = ', '.join(f"`{column}`" for column in insert_columns)
                placeholder_sql = ', '.join(['%s'] * len(insert_columns))

                # 使用参数化 SQL，把用户输入交给驱动处理，避免拼接 SQL 带来的注入风险。
                cursor.execute(
                    f"INSERT INTO `{USER_TABLE_NAME}` ({column_sql}) VALUES ({placeholder_sql})",
                    tuple(insert_values)
                )
                insert_id = cursor.lastrowid
            conn.commit()
    except MySQLError as e:
        return api_response(code=500, message=f'数据库写入失败：{e}', data=None)

    return api_response(message='提交成功!', data=True)


if __name__ == '__main__':
    app.run(debug=True)
