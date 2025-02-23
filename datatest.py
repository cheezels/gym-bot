import os
from datetime import datetime, timedelta

import mysql.connector
import json

database = mysql.connector.connect(
    host = 'localhost',
    user = 'user',
    password = 'password123!',
    database = 'gymeRHbot'
   )

config = {
    "host": "0.0.0.0",
    "port": 3306,
    "user": "root@gymeRHbot.com",
    "password": "",
}

cursor = database.cursor()
database.autocommit = True

def enter_gymdb(id, timeIn) -> bool:
    update()
    query = f"""
            SELECT id, Time_in
            FROM gymeRHbot.users
            WHERE id = '{id}' AND Time_out IS NULL;
        """
    cursor.execute(query)
    result = cursor.fetchone()

    # user alr in jim
    if result:
        return False

    query = f"INSERT INTO gymeRHbot.users(id, Time_in, Time_out)VALUES({id},'{timeIn}',DEFAULT);"
    cursor.execute(query)
    return True

def exit_gymdb(id, timeOut) -> bool:
    update()

    query = f"UPDATE gymeRHbot.users SET Time_out = '{timeOut}' WHERE id = {id};"
    cursor.execute(query)
    query2 = f"SELECT * FROM gymeRHbot.users WHERE id = {id};"
    cursor.execute(query2)
    result = cursor.fetchone()

    # user not in jim
    if not result:
        return False

    query_transfer = """
                INSERT INTO gymeRHbot.history (id, Time_in, Time_out)
                SELECT id, Time_in, Time_out
                FROM gymeRHbot.users
                WHERE Time_out IS NOT NULL;
            """
    cursor.execute(query_transfer)

    query_remove_from_users = """
                DELETE FROM gymeRHbot.users
                WHERE Time_out IS NOT NULL;
            """
    cursor.execute(query_remove_from_users)
    return True


def check_capacitydb() -> json:
    update()
    # query = f"SELECT JSON_OBJECT ('"'Time in'"', Time_in, '"'Time out'"', Time_out)FROM gymeRHbot.users WHERE '"'Time out'"' IS NOT NULL;"
    # cursor.execute(query)
    # output = cursor.fetchall()
    # return output
    query = f"SELECT COUNT(*) FROM gymeRHbot.users WHERE Time_out IS NULL;"
    cursor.execute(query)
    result = cursor.fetchone()
    return result[0]

def check_historydb() -> json:
    update()
    query = f"SELECT JSON_OBJECT ('"'ID'"', id, '"'Time in'"', Time_in, '"'Time out'"', Time_out)FROM gymeRHbot.history"
    cursor.execute(query)
    output = cursor.fetchall()
    return output

def test(i, timeIn) -> json:
    query = f"INSERT INTO gymeRHbot.users(ID, Time_in, Time_out)VALUES({i},'{timeIn}',DEFAULT);"
    cursor.execute(query)
    query2 = f"SELECT JSON_OBJECT ('"'ID'"', id, '"'Time in'"', Time_in, '"'Time out'"', Time_out)FROM gymeRHbot.history"
    cursor.execute(query2)
    output = cursor.fetchall()
    return output

def update() -> None:
    # kick people out if they forgor
    current_time = datetime.now()
    query = """
        SELECT ID, Time_in 
        FROM gymeRHbot.users 
        WHERE Time_out IS NULL;
        """
    cursor.execute(query)
    users = cursor.fetchall()

    for user in users:
        user_id = user[0]
        time_in = user[1]
        #time_in = datetime.strftime(time_in, "%Y-%m-%d %H:%M:%S")
        timeout = time_in + timedelta(hours=3)

        if current_time > timeout:
            query_update = f"""
                UPDATE gymeRHbot.users 
                SET Time_out = '{timeout.strftime('%Y-%m-%d %H:%M:%S')}'
                WHERE ID = {user_id};
                """
            cursor.execute(query_update)

    # trsf people dat leaf alr frm users to history
    query_transfer = """
            INSERT INTO gymeRHbot.history (ID, Time_in, Time_out)
            SELECT id, Time_in, Time_out
            FROM gymeRHbot.users
            WHERE Time_out IS NOT NULL AND Time_out < NOW();
        """
    cursor.execute(query_transfer)

    query_remove_from_users = """
            DELETE FROM gymeRHbot.users
            WHERE Time_out IS NOT NULL AND Time_out < NOW();
        """
    cursor.execute(query_remove_from_users)
