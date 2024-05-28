#数据库连接配置
import pymysql

conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='Maoyurui20041023',
        database='personal'
    )