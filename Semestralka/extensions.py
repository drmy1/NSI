from typing import Dict
import json
import pandas as pd
from db import insert_data_into_db, create_data_table
from flask import session
import ipaddress
import logging
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


limiter = Limiter(key_func=get_remote_address, default_limits=["5 per second"])

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


def jsonify_data() -> Dict[str, Dict[str, str]] | None:
    """
    {
    0: {'temperature': 21, 'timestamp': Timestamp('2025-01-01 01:00:00+0000', tz='UTC')},
    1: {'temperature': 33, 'timestamp': Timestamp('2025-01-01 01:05:52+0000', tz='UTC')},
    2: {'temperature': 38, 'timestamp': Timestamp('2025-01-01 01:10:23+0000', tz='UTC')},
    }
    """
    with open("data.txt", "r") as f:
        create_data_table()
        try:
            if f.readable():
                for line in f.readlines():
                    if len(line.strip("DAT=[]\n")) == 0:
                        continue
                    else:
                        line = line.strip("\n").strip(",").replace("    ", "")
                        id_ = dict(json.loads(line))["id"]
                        temperature = dict(json.loads(line))["temperature"]
                        timestamp = dict(json.loads(line))["timestamp"]
                        insert_data_into_db(
                            id_,
                            json.dumps(
                                {"temperature": temperature, "timestamp": timestamp}
                            ),
                        )
            else:
                logging.error("File is not readable")
                raise ValueError("File is not readable")
        except Exception as e:
            logging.error("Error reading file: %s", e)
            print(e)

        return None


def parse_time(time_str):
    return pd.to_datetime(time_str, utc=True)


def logged_in():
    if session:
        return True
    return False


def is_valid_ipv4(ip_object):
    """
    Checks if the given object is a valid IPv4 address.

    Parameters:
    - ip_object: The object to be checked for validity as an IPv4 address.

    Returns:
    - True if the object is a valid IPv4 address, False otherwise.

    Raises:
    - None.

    Examples:
    - is_valid_ipv4("192.168.0.1") returns True
    - is_valid_ipv4("256.0.0.1") returns False
    - is_valid_ipv4("192.168.0") returns False
    """
    try:
        ipaddress.IPv4Address(ip_object)
        return True
    except (ValueError, TypeError):
        return False
