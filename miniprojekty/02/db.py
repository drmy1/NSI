import sqlite3

CREATE_DATA_TABLE = "CREATE TABLE IF NOT EXISTS Data (id INTEGER PRIMARY KEY, temperature_timestamp TEXT)"
CREATE_USERS_TABLE = "CREATE TABLE IF NOT EXISTS Users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)"
SELECT_USER_DATA_FROM_TABLE = "SELECT * FROM Users WHERE username = ? AND password = ?"
SELECT_MAX_ID_FROM_USERS = "SELECT MAX(id) FROM Users"
INSERT_CREDS_INTO_DB = "INSERT INTO Users (username, password) VALUES (?, ?)"
INSERT_DATA_INTO_DB = "INSERT INTO Data (id, temperature_timestamp) VALUES (?, ?) ON CONFLICT (id) DO NOTHING"
SELECT_MAX_ID_FROM_DATA_TABLE = "SELECT MAX(id) FROM Data"
SELECT_NUM_ROWS = "SELECT id, temperature_timestamp FROM (SELECT id, temperature_timestamp FROM data ORDER BY id DESC LIMIT ?) AS subquery ORDER BY id ASC;"
SELECT_DATA_BY_ID = "SELECT id, temperature_timestamp FROM Data WHERE id = ?"
DELETE_DATA_BY_ID = "DELETE FROM Data WHERE id = ?"
SELECT_MIN_ID_FROM_DATA_TABLE = "SELECT MIN(id) FROM Data"
SELECT_ALL_DATA_DESC = "SELECT id, temperature_timestamp FROM Data ORDER BY id DESC"
SELECT_ALL_DATA_ASC = "SELECT id, temperature_timestamp FROM Data ORDER BY id ASC"

def create_data_table():
    connection = sqlite3.connect("miniproject.db")
    cur = connection.cursor()
    cur.execute(CREATE_DATA_TABLE)
    connection.commit()
    cur.close()


def create_users_table():
    connection = sqlite3.connect("miniproject.db")
    cur = connection.cursor()
    cur.execute(CREATE_USERS_TABLE)
    connection.commit()
    cur.close()


def fetch_max_id_from_users():
    connection = sqlite3.connect("miniproject.db")
    cur = connection.cursor()
    cur.execute(SELECT_MAX_ID_FROM_USERS)
    max_id = cur.fetchone()[0]
    cur.close()
    return max_id


def fetch_max_id_from_data():
    connection = sqlite3.connect("miniproject.db")
    cur = connection.cursor()
    cur.execute(SELECT_MAX_ID_FROM_DATA_TABLE)
    max_id = cur.fetchone()[0]
    cur.close()
    return max_id


def insert_creds_into_db(username, password):
    connection = sqlite3.connect("miniproject.db")
    cur = connection.cursor()
    cur.execute(INSERT_CREDS_INTO_DB, (username, password))
    connection.commit()
    cur.close()


def fetch_user_data_from_table(username, password):
    connection = sqlite3.connect("miniproject.db")
    cur = connection.cursor()
    cur.execute(SELECT_USER_DATA_FROM_TABLE, (username, password))
    creds = cur.fetchone()[1:3]
    cur.close()
    return (creds[0], creds[1])


def insert_data_into_db(id_, temperature_timestamp):
    connection = sqlite3.connect("miniproject.db")
    cur = connection.cursor()
    cur.execute(INSERT_DATA_INTO_DB, (id_, temperature_timestamp))
    connection.commit()
    cur.close()


def fetch_data_from_db(num):
    connection = sqlite3.connect("miniproject.db")
    cur = connection.cursor()
    cur.execute(SELECT_NUM_ROWS, (num,))
    data = cur.fetchall()
    cur.close()
    return data

def fetch_data_by_id(id_):
    connection = sqlite3.connect("miniproject.db")
    cur = connection.cursor()
    cur.execute(SELECT_DATA_BY_ID, (id_,))
    data = cur.fetchall()
    cur.close()
    return data

def delete_data_by_id(id_):
    connection = sqlite3.connect("miniproject.db")
    cur = connection.cursor()
    cur.execute(DELETE_DATA_BY_ID, (id_,))
    connection.commit()
    cur.close()
    
def fetch_min_data_from_table():
    connection = sqlite3.connect("miniproject.db")
    cur = connection.cursor()
    cur.execute(SELECT_MIN_ID_FROM_DATA_TABLE)
    min_id = cur.fetchone()[0]
    cur.close()
    return min_id

def fetch_all_data_by_order(order):
    connection = sqlite3.connect("miniproject.db")
    cur = connection.cursor()
    match order:
        case "asc":
            cur.execute(SELECT_ALL_DATA_ASC)
        case "desc":
            cur.execute(SELECT_ALL_DATA_DESC)
    data = cur.fetchall()
    cur.close()
    return data