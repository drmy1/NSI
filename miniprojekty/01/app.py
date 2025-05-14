from typing import Dict
import json
from flask import Flask, render_template, request, redirect, url_for, jsonify
import pandas as pd

app = Flask(__name__)  # Creating an instance of the Flask class


def jsonify_data() -> Dict[str, Dict[str, str]] | None:
    data: Dict[str, Dict[str, str]] = dict()
    with open("data.txt", "r") as f:
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
                        data[id_] = {
                            "temperature": temperature,
                            "timestamp": parse_time(timestamp),
                        }

                return data
            else:
                raise ValueError("File is not readable")
        except Exception as e:
            print(e)

        return None


@app.route("/parametrization", methods=["GET", "POST"])
def get_last_measurements():
    global DATA
    DATA = jsonify_data()

    num = int(request.args.get("num", 15))
    last_entries = {key: DATA[key] for key in list(DATA.keys())[-num:]}

    DATA = last_entries
    if len(DATA) < num:
        return jsonify({"error": "Dont have enough data"}), 400

    return jsonify(list(DATA.values()))


@app.route("/delete_one", methods=["POST", "GET"])
def delete_one_data_point():
    global DATA

    if not DATA:
        return jsonify({"error": "No data to delete"}), 400

    first_key = next(iter(DATA))
    del DATA[first_key]

    return jsonify(list(DATA.values()))


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    get_last_measurements()
    return render_template("dashboard.html", data=DATA.values())


@app.route("/login", methods=["GET", "POST"])
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == "admin" and password == "admin":
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    return render_template("register.html")


def parse_time(time_str):
    return pd.to_datetime(time_str, utc=True)


if __name__ == "__main__":
    # DATA = jsonify_data()
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)
