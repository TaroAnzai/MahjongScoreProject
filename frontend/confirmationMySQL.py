import pymysql

conn = pymysql.connect(
    host='localhost',
    user='mahjong_user',
    password='Taro58009@',
    database='mahjongscore',
    charset='utf8mb4'
)

with conn.cursor() as cursor:
    cursor.execute("SELECT DATABASE();")
    print("接続成功：", cursor.fetchone()[0])
