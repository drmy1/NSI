from typing import Dict
import json
import pandas as pd
from db import insert_data_into_db, create_data_table, fetch_max_id_from_users
from flask import session, redirect


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
                raise ValueError("File is not readable")
        except Exception as e:
            print(e)

        return None


def parse_time(time_str):
    return pd.to_datetime(time_str, utc=True)


def logged_in():
    if session:
        return True
    return False