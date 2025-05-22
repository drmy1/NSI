from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    url_for,
    jsonify,
    session,
    Response,
)
import json
from db import (
    create_users_table,
    fetch_user_data_from_table,
    fetch_max_id_from_users,
    insert_creds_into_db,
    fetch_data_from_db,
    fetch_max_id_from_data,
    fetch_data_by_id,
    delete_data_by_id,
    fetch_min_data_from_table,
    insert_data_into_db,
    fetch_all_data_by_order,
)
from typing import Dict
from extensions import jsonify_data, logged_in
import base64
from datetime import datetime
import logging
import queue
import time
from utills import message_queue, mqtt_client_handler

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


NOT_LOGGED_IN = "User not logged in - redirecting to login"

creds = Blueprint("creds", __name__)
data_manipulation = Blueprint("data_manipulation", __name__)
dash = Blueprint("dash", __name__)
terminal_bp = Blueprint("terminal_bp", __name__)
meteo_bp = Blueprint("meteo_bp", __name__)


@creds.route("/login", methods=["GET", "POST"])
def login():
    jsonify_data()
    create_users_table()
    if not fetch_max_id_from_users():
        logging.info("No users found - redirecting to register")
        return redirect("/api/register")
    if request.method == "GET":
        if session:
            logging.info("User already logged in - redirecting to dashboard")
            return redirect(url_for("dash.dashboard"))
    if request.method == "POST":
        creds: Dict[str, str] = dict()
        creds = {
            "username": request.form.get("username"),
            "password": request.form.get("password"),
        }
        try:
            creds["password"] = base64.b64encode(creds["password"].encode()).decode()
            if fetch_user_data_from_table(creds["username"], creds["password"]):
                session["username"] = creds["username"] + creds["password"]
                logging.info(f"User {creds['username']} logged in successfully")
                return redirect(url_for("dash.dashboard"))
        except Exception:
            logging.error("Error during login", exc_info=True)
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")


@data_manipulation.route("/parametrization", methods=["GET", "POST"])
def get_last_measurements():
    if not logged_in():
        logging.info(NOT_LOGGED_IN)
        return redirect("/api/login")
    global DATA
    num = int(request.args.get("num", 15))
    DATA = fetch_data_from_db(num)

    last_entries = {row[0]: json.loads(row[1]) for row in DATA}
    DATA = last_entries

    if len(DATA) < num:
        logging.info("Not enough datapints to display")
        return jsonify({"error": "Dont have enough data"}), 400

    return jsonify(list(last_entries.values()))


@data_manipulation.route("/display_all_data", methods=["GET", "POST"])
def get_all():
    arg = request.args.get("order")
    arg2 = request.args.get("form")
    if arg2 is not None:
        try:
            arg2 = int(arg2)
        except ValueError:
            return jsonify({"error": "Invalid form"}), 400
    match arg2:
        case 0:
            order = arg
            data = fetch_all_data_by_order(order)
            data = {row[0]: json.loads(row[1]) for row in data}
            return render_template("dashboard.html", data=data.values())
        case _:
            order = arg
            data = fetch_all_data_by_order(order)
            data = {row[0]: json.loads(row[1]) for row in data}
            return jsonify(list(data.values()))


@data_manipulation.route("/delete_one", methods=["POST", "GET"])
def delete_one_data_point():
    global DATA

    if not DATA:
        logging.info("No data to delete")
        return jsonify({"error": "No data to delete"}), 400

    first_key = next(iter(DATA))
    del DATA[first_key]
    logging.info(f"Deleted data point with ID: {first_key}")
    return jsonify(list(DATA.values()))


@data_manipulation.route("/get_last_data_point", methods=["POST", "GET"])
@data_manipulation.route("/fetch_data_by_id", methods=["POST", "GET"])
def data_by_id():
    max_id = fetch_max_id_from_data()
    form = request.form.get("id")
    arg = request.args.get("id")
    if form:
        if not logged_in():
            logging.info(NOT_LOGGED_IN)
            return redirect("/api/login")
        id_ = form
    elif arg:
        id_ = arg
    else:
        id_ = max_id
    id_ = int(id_)
    if id_ > max_id:
        logging.info("No such data")
        return jsonify({"error": "No such data"}), 400
    fetdata = fetch_data_by_id(id_)
    if not fetdata:
        logging.info("No such data")
        return jsonify({"error": "No such data"}), 400
    data = {row[0]: json.loads(row[1]) for row in fetdata}
    logging.info(f"Fetched data point with ID: {id_}")
    return jsonify(list(data.values()))


@data_manipulation.route("/delete_data_by_id", methods=["POST", "GET"])
@data_manipulation.route("/delete_oldest_data_point", methods=["POST", "GET"])
def fdelete_data_by_id():
    max_id = fetch_max_id_from_data()
    min_id = fetch_min_data_from_table()
    form = request.form.get("id")
    arg = request.args.get("id")
    if form:
        if not logged_in():
            logging.info(NOT_LOGGED_IN)
            return redirect("/api/login")
        id_ = form
    elif arg:
        id_ = arg
    else:
        id_ = min_id
    id_ = int(id_)
    if id_ > max_id:
        logging.info("No such data")
        return jsonify({"error": "No such data"}), 400
    delete_data_by_id(id_)
    logging.info(f"Deleted data point with ID: {id_}")
    return jsonify({"success": "Data deleted"})


@data_manipulation.route("/add_new_data_by_temp", methods=["POST", "GET"])
def add_data_by_temp():
    form = request.form.get("temp")
    arg = request.args.get("temp")
    if form:
        if not logged_in():
            logging.info(NOT_LOGGED_IN)
            return redirect("/api/login")
        temperature = form
    else:
        temperature = arg
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not int(temperature):
        logging.warning("Invalid temperature value")
        return jsonify({"error": "Invalid temperature"}), 400
    id_ = fetch_max_id_from_data() + 1
    insert_data_into_db(
        id_, json.dumps({"temperature": int(temperature), "timestamp": timestamp})
    )
    logging.info(f"Added new data point with ID: {id_} and temperature: {temperature}")
    return jsonify({"success": "Data added"})


@dash.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if not logged_in():
        logging.info(NOT_LOGGED_IN)
        return redirect("/api/login")
    get_last_measurements()
    logging.info("Displaying dashboard")
    return render_template(
        "dashboard.html", data=DATA.values(), active_page="dashboard"
    )


@creds.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        creds: Dict[str, str] = dict()
        creds = {
            "username": request.form.get("username"),
            "password": request.form.get("password"),
        }
        insert_creds_into_db(
            creds["username"], base64.b64encode(creds["password"].encode()).decode()
        )
        session["username"] = creds["username"] + creds["password"]
        logging.info(f"User {creds['username']} registered successfully")
        return redirect("/api/login")
    logging.info("Displaying registration page")
    return render_template("register.html")


@terminal_bp.route("/terminal", methods=["GET", "POST"])
def terminal_page():
    if not logged_in():
        logging.info(NOT_LOGGED_IN)
        return redirect("/api/login")
    logging.info("Displaying terminal page")
    return render_template("terminal.html", active_page="terminal")


@terminal_bp.route("/mqtt-message", methods=["POST"])
def receive_mqtt_message():
    data = request.json
    if data and "topic" in data and "payload" in data:
        logging.info(
            f"Flask received message via HTTP POST: {data['topic']} {data['payload']}"
        )
        # Use the message_queue from extensions
        message_queue.put(
            {
                "topic": data["topic"],
                "payload": data["payload"],
                "qos": data.get("qos", 0),
            }
        )
        return jsonify(status="success", message="Message received by HTTP POST"), 200
    else:
        logging.warning("Flask received invalid message format via HTTP POST")
        return jsonify(
            status="error", message="Invalid message format for HTTP POST"
        ), 400


@terminal_bp.route("/terminal-stream")
def terminal_stream():
    def event_stream():
        while True:
            try:
                message = message_queue.get(timeout=0.1)
                formatted_message = f" QoS: {message['qos']} || topic: {message['topic']} || message: {message['payload']}"
                # Send data in SSE format
                yield f"data: {formatted_message}\n\n"
                message_queue.task_done()
            except queue.Empty:
                # Send a comment to keep the connection alive if no message
                yield ": keepalive\n\n"
            time.sleep(0.1)

    return Response(event_stream(), mimetype="text/event-stream")


@terminal_bp.route("/send-mqtt-message", methods=["POST"])
def send_mqtt_message_route():
    if not logged_in():
        logging.warning("Attempt to send MQTT message while not logged in.")
        return jsonify(status="error", message="User not logged in"), 401

    data = request.json
    topic = data.get("topic")
    payload = data.get("payload")
    qos = data.get("qos", 0)

    if not topic or payload is None:
        logging.warning(
            f"Missing topic or payload for sending MQTT message. Data: {data}"
        )
        return jsonify(status="error", message="Topic and payload are required"), 400

    try:
        qos = int(qos)
        if qos not in [0, 1, 2]:
            logging.warning(f"Invalid QoS value: {qos}. Defaulting to 0.")
            qos = 0
    except ValueError:
        logging.warning(f"QoS value not an integer: {qos}. Defaulting to 0.")
        qos = 0

    # Use the imported mqtt_client_handler from utills.py
    if not mqtt_client_handler or not mqtt_client_handler.client.is_connected():
        logging.error("MQTT client (from utills) not connected. Cannot send message.")
        # Optional: Attempt to reconnect, but this should ideally be managed globally
        # mqtt_client_handler.connect()
        # if not mqtt_client_handler.client.is_connected():
        #     return jsonify(status="error", message="MQTT client reconnection failed"), 503
        return jsonify(status="error", message="MQTT client not connected"), 503

    try:
        success = mqtt_client_handler.publish_message(topic, payload, qos)
        if success:
            logging.info(
                f"Successfully published MQTT message to topic '{topic}' via shared client: {payload}"
            )
            return jsonify(status="success", message="Message published"), 200
        else:
            logging.error(
                f"Failed to publish MQTT message to topic '{topic}' via shared client."
            )
            return jsonify(status="error", message="Failed to publish message"), 500
    except Exception as e:
        logging.error(
            f"Exception when trying to publish MQTT message via shared client: {e}",
            exc_info=True,
        )
        return jsonify(status="error", message=f"Server error: {e}"), 500


@meteo_bp.route("/meteo", methods=["GET", "POST"])
def meteo():
    if not logged_in():
        logging.info(NOT_LOGGED_IN)
        return redirect("/api/login")
    logging.info("Displaying meteo page")
    return render_template("meteo.html", active_page="meteo")
