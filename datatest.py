import os
import mysql.connector
import json

database = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    password = 'mysql_Jarvis8002',
    database = 'gymeRHbot'
   )

config = {
    "host": "0.0.0.0",
    "port": 3306,
    "user": "root@gymeRHbot.com",
    "password": "mysql_Jarvis8002",
}

database.autocommit = True

def enter_gymdb(id, timeIn) -> None:
    query = f"INSERT INTO gymeRHbot.users(ID, Time_in, Time_out)VALUES({id},'{timeIn}',DEFAULT);"
    cursor.execute(query)

def exit_gymdb(id, timeOut) -> None:
    query = f"UPDATE gymeRHbot.users SET Time_out = '{timeOut}' WHERE id = {id};"
    cursor.execute(query)

def check_capacitydb() -> json:
    query = f"SELECT JSON_OBJECT ('"'Time in'"', Time_in, '"'Time out'"', Time_out)FROM gymeRHbot.users WHERE '"'Time out'"' IS NOT NULL;"
    cursor.execute(query)
    output = cursor.fetchall()
    return output

cursor = database.cursor()

#cursor.execute("SELECT * FROM gymeRHbot.users")
ans = check_capacitydb()
for user in ans:
    print(ans)