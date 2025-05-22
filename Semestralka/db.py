import sqlite3
import logging
import json  # Added for parsing temperature_timestamp if it's stored as JSON
from typing import Optional

logging.basicConfig(
    level=logging.INFO,  # Set the logging level to DEBUG
    # level=logging.DEBUG,
    # Define the format of log messages
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="app.log",  # Specify the file to write logs to
    # Specify the file writing mode ('w' for overwrite, 'a' for append)
    filemode="a",
    encoding="utf8",
)

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
METEO_DEVICE_TABLE_PREFIX = "meteo_device_"


def create_data_table():
    connection = sqlite3.connect("miniproject.db")
    cur = connection.cursor()
    cur.execute(CREATE_DATA_TABLE)
    connection.commit()
    cur.close()
    logging.info("Data table created")


def create_users_table():
    connection = sqlite3.connect("miniproject.db")
    cur = connection.cursor()
    cur.execute(CREATE_USERS_TABLE)
    connection.commit()
    cur.close()
    logging.info("Users table created")


def fetch_max_id_from_users():
    connection = sqlite3.connect("miniproject.db")
    cur = connection.cursor()
    cur.execute(SELECT_MAX_ID_FROM_USERS)
    max_id = cur.fetchone()[0]
    cur.close()
    logging.info("Max ID from users table fetched")
    return max_id


def fetch_max_id_from_data():
    connection = sqlite3.connect("miniproject.db")
    cur = connection.cursor()
    cur.execute(SELECT_MAX_ID_FROM_DATA_TABLE)
    max_id = cur.fetchone()[0]
    cur.close()
    logging.info("Max ID from data table fetched")
    return max_id


def insert_creds_into_db(username, password):
    connection = sqlite3.connect("miniproject.db")
    cur = connection.cursor()
    cur.execute(INSERT_CREDS_INTO_DB, (username, password))
    connection.commit()
    cur.close()
    logging.info("Credentials inserted into database")


def fetch_user_data_from_table(username, password):
    connection = sqlite3.connect("miniproject.db")
    cur = connection.cursor()
    cur.execute(SELECT_USER_DATA_FROM_TABLE, (username, password))
    creds = cur.fetchone()[1:3]
    cur.close()
    logging.info(f"User ({creds[0]}) data fetched from table")
    return (creds[0], creds[1])


def insert_data_into_db(id_, temperature_timestamp):
    connection = sqlite3.connect("miniproject.db")
    cur = connection.cursor()
    cur.execute(INSERT_DATA_INTO_DB, (id_, temperature_timestamp))
    connection.commit()
    cur.close()
    logging.info(f"Data inserted into database with ID: {id_}")


def fetch_data_from_db(num):
    connection = sqlite3.connect("miniproject.db")
    cur = connection.cursor()
    cur.execute(SELECT_NUM_ROWS, (num,))
    data = cur.fetchall()
    cur.close()
    logging.info(f"Fetched {num} rows from data table")
    return data


def fetch_data_by_id(id_):
    connection = sqlite3.connect("miniproject.db")
    cur = connection.cursor()
    cur.execute(SELECT_DATA_BY_ID, (id_,))
    data = cur.fetchall()
    cur.close()
    logging.info(f"Fetched data point with ID: {id_}")
    return data


def delete_data_by_id(id_):
    connection = sqlite3.connect("miniproject.db")
    cur = connection.cursor()
    cur.execute(DELETE_DATA_BY_ID, (id_,))
    connection.commit()
    cur.close()
    logging.info(f"Deleted data point with ID: {id_}")


def fetch_min_data_from_table():
    connection = sqlite3.connect("miniproject.db")
    cur = connection.cursor()
    cur.execute(SELECT_MIN_ID_FROM_DATA_TABLE)
    min_id = cur.fetchone()[0]
    cur.close()
    logging.info("Min ID from data table fetched")
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
    logging.info(f"Fetched all data in {order} order")
    return data


def create_meteo_device_table(device_id: int):
    """Creates a new table for a meteo device if it doesn't exist."""
    table_name = f"{METEO_DEVICE_TABLE_PREFIX}{device_id}"
    connection = sqlite3.connect("miniproject.db")
    cur = connection.cursor()
    try:
        # id will be auto-incrementing for each device's readings
        # timestamp will store the time of the reading
        # temperature will store the temperature value
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                temperature REAL NOT NULL
            )
        """)
        connection.commit()
        logging.info(
            f"Table {table_name} created or already exists for meteo device {device_id}."
        )
        return True
    except sqlite3.Error as e:
        logging.error(f"Error creating table {table_name}: {e}")
        return False
    finally:
        cur.close()
        connection.close()


def insert_meteo_device_reading(device_id: int, timestamp: str, temperature: float):
    """Inserts a new temperature reading for a specific meteo device."""
    table_name = f"{METEO_DEVICE_TABLE_PREFIX}{device_id}"
    connection = sqlite3.connect("miniproject.db")
    cur = connection.cursor()
    try:
        cur.execute(
            f"INSERT INTO {table_name} (timestamp, temperature) VALUES (?, ?)",
            (timestamp, temperature),
        )
        connection.commit()
        logging.info(
            f"Inserted reading into {table_name}: Time={timestamp}, Temp={temperature}"
        )
        return True
    except sqlite3.Error as e:
        logging.error(f"Error inserting reading into {table_name}: {e}")
        return False
    finally:
        cur.close()
        connection.close()


def fetch_meteo_device_data(device_id: int, limit: Optional[int] = None):
    """Fetches data for a specific meteo device, optionally limited."""
    table_name = f"{METEO_DEVICE_TABLE_PREFIX}{device_id}"
    connection = sqlite3.connect("miniproject.db")
    cur = connection.cursor()
    try:
        query = f"SELECT timestamp, temperature FROM {table_name} ORDER BY timestamp ASC"  # Fetch in chronological order
        if limit and isinstance(limit, int) and limit > 0:
            query += f" LIMIT {limit}"
        cur.execute(query)
        data = cur.fetchall()  # Should be a list of sqlite3.Row objects
        logging.info(f"Fetched {len(data)} readings from {table_name}")
        return [
            dict(row) for row in data
        ]  # Convert list of sqlite3.Row to list of dicts
    except sqlite3.Error as e:
        # This will also catch cases where the table doesn't exist
        logging.warning(f"Could not fetch data from {table_name}: {e}")
        return []  # Return empty list if table doesn't exist or other error
    finally:
        cur.close()
        connection.close()


def get_existing_meteo_device_ids():
    """Returns a list of existing meteo device IDs by inspecting table names."""
    connection = sqlite3.connect("miniproject.db")
    cur = connection.cursor()
    try:
        # Querying sqlite_master for table names.
        # The 'name' column is the first column (index 0).
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE ?",
            (f"{METEO_DEVICE_TABLE_PREFIX}%",),
        )
        tables = (
            cur.fetchall()
        )  # This will be a list of tuples (or sqlite3.Row objects if factory works)
        device_ids = []
        for table_row in tables:  # table_row is a single row from the fetchall result
            try:
                # Access the table name by index 0, as it's the first column selected.
                # This is safer if row_factory isn't consistently returning dict-like rows.
                table_name_str = table_row[0]
                device_id = int(table_name_str.replace(METEO_DEVICE_TABLE_PREFIX, ""))
                device_ids.append(device_id)
            except (
                ValueError,
                TypeError,
                IndexError,
            ) as e:  # Catch potential errors during parsing
                # Log the problematic row and the error
                logging.warning(
                    f"Found table row '{table_row}' matching prefix but could not parse ID. Error: {e}"
                )
        device_ids.sort()  # Ensure they are in order
        logging.info(f"Found existing meteo device IDs: {device_ids}")
        return device_ids
    except sqlite3.Error as e:
        logging.error(f"Error fetching meteo device tables: {e}")
        return []
    finally:
        cur.close()
        connection.close()


def get_next_meteo_device_id():
    """Determines the next available ID for a new meteo device."""
    existing_ids = get_existing_meteo_device_ids()
    if not existing_ids:
        return 1
    return max(existing_ids) + 1
