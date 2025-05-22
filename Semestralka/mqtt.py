import paho.mqtt.client as mqtt  # type: ignore
import logging
import os
from extensions import is_valid_ipv4
from dotenv import load_dotenv
import requests  # type: ignore
from datetime import datetime
import json
from db import (
    get_existing_meteo_device_ids,
    insert_meteo_device_reading,
)

logging.basicConfig(
    level=logging.INFO,
    # level=logging.DEBUG,
    # Define the format of log messages
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="app.log",
    filemode="a",
    encoding="utf8",
)


class Env:
    load_dotenv()

    def __init__(self, host=None, port=None, user=None, passw=None):
        self._host = host
        self._port = port
        self._user = user
        self._passw = passw

    @property
    def gethost(self):
        if self._host is None:
            self._host = os.environ.get("MQTT_BROKER_HOST")
        return self._host

    @gethost.setter
    def gethost(self, val):
        if val is not None:
            if not is_valid_ipv4(val):
                raise ValueError("Invalid IP address")
            self._host = val
        else:
            raise ValueError("Host cannot be None")

    @property
    def getport(self):
        if self._port is None:
            self._port = os.environ.get("MQTT_BROKER_PORT")
        return int(self._port)

    @getport.setter
    def getport(self, val):
        if val is not None:
            try:
                val = int(val)
                if not (0 < val < 65536):
                    raise ValueError("Port must be between 1 and 65535")
                self._port = val
            except ValueError:
                raise ValueError("Port must be an integer")
        else:
            raise ValueError("Port cannot be None")

    @property
    def getuser(self):
        if self._user is None:
            self._user = os.environ.get("MQTT_USERNAME")
        return self._user

    @getuser.setter
    def getuser(self, val):
        if val is not None:
            self._user = val
        else:
            raise ValueError("User cannot be None")

    @property
    def getpassword(self):
        if self._passw is None:
            self._passw = os.environ.get("MQTT_PASSWORD")
        return self._passw

    @getpassword.setter
    def getpassword(self, val):
        if val is not None:
            self._passw = val
        else:
            raise ValueError("Password cannot be None")


class Mqtt:
    subscribed = False
    FLASK_MESSAGE_ENDPOINT = "https://127.0.0.1:5000/api/mqtt-message"

    def __init__(self):
        self.client = mqtt.Client(clean_session=True, client_id="NSI_semestralka")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        # TODO For the future maybe
        # self.client.on_publish = self.on_publish
        # self.client.on_subscribe = self.on_subscribe
        # self.client.on_log = self.on_log
        env_settings = Env()
        self.username = env_settings.getuser
        self.password = env_settings.getpassword
        self.host = env_settings.gethost
        self.port = env_settings.getport
        self.topics_to_subscribe = [("#", 2)]

    @classmethod
    def setsub(cls) -> None:
        logging.info("Setting subscription to True")
        cls.subscribed = True

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logging.info(f"Subscribing to topics: {self.topics_to_subscribe}")
            client.subscribe(self.topics_to_subscribe)

        else:
            logging.error(f"Connection failed, not subscribing. Result code: {rc}")
        logging.info(f"Connected with result code {rc}")

    def on_message(self, client, userdata, msg):
        if not self.subscribed:
            logging.info("Program started, configuring subscription...")
            self.setsub()

        topic = msg.topic
        try:
            message_content_str = msg.payload.decode()

            logging.info(f"Message received: {topic} {message_content_str}")
        except UnicodeDecodeError:
            logging.error(
                f"Could not decode payload for topic {topic}. Payload: {msg.payload}"
            )

            return

        # --- Logic for /meteo/* topics (database insertion) ---
        if topic.startswith("/meteo/"):
            parts = topic.split("/")
            if len(parts) == 3 and parts[1] == "meteo":
                try:
                    device_id_str = parts[2]
                    device_id = int(device_id_str)
                except ValueError:
                    logging.warning(
                        f"Invalid device ID format in topic: {topic}. Expected integer."
                    )

                if "device_id" in locals() or "device_id" in globals():
                    try:
                        payload_data = json.loads(message_content_str)
                        temperature = payload_data.get("temperature")
                        timestamp_str = payload_data.get("timestamp")
                        if timestamp_str:
                            pass
                        else:
                            timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                        if temperature is None:
                            logging.warning(
                                f"No 'temperature' field in payload for {topic}: {message_content_str}"
                            )

                        else:
                            temperature = float(temperature)
                            existing_device_ids = get_existing_meteo_device_ids()
                            if device_id in existing_device_ids:
                                logging.info(
                                    f"Device ID {device_id} found in DB. Inserting data: T={temperature}, Time={timestamp_str}"
                                )
                                if insert_meteo_device_reading(
                                    device_id, timestamp_str, temperature
                                ):
                                    logging.info(
                                        f"Successfully inserted data for meteo device {device_id}."
                                    )
                                else:
                                    logging.error(
                                        f"Failed to insert data for meteo device {device_id}."
                                    )
                            else:
                                logging.warning(
                                    f"Meteo device ID {device_id} from topic {topic} not found in the database. Data not inserted."
                                )

                    except json.JSONDecodeError:
                        logging.error(
                            f"Could not parse JSON payload for meteo device {device_id_str} on topic {topic}: {message_content_str}"
                        )

                    except ValueError:
                        logging.error(
                            f"Invalid temperature format for meteo device {device_id_str} on topic {topic}. Expected float."
                        )

                    except Exception as e:
                        logging.error(
                            f"Error processing meteo payload for {topic}: {e}"
                        )

            else:
                logging.warning(
                    f"Received message on a /meteo/ topic with unexpected structure: {topic}"
                )

        if self.subscribed:
            try:
                requests.post(
                    self.FLASK_MESSAGE_ENDPOINT,
                    json={
                        "topic": topic,
                        "payload": message_content_str,
                        "qos": msg.qos,
                    },
                    verify=False,
                )
                logging.info(f"Message sent to Flask: {topic} {message_content_str}")
            except requests.exceptions.RequestException as e:
                logging.error(f"Error sending message to Flask: {e}")

    # TODO For the future maybe
    # def on_publish(self, client, userdata, mid):
    #     logging.info(f"Message published: {mid}")
    #     print(f"Message published: {mid}")

    # def on_subscribe(self, client, userdata, mid, granted_qos):
    #     logging.info(f"Subscribed: {mid} {granted_qos}")
    #     print(f"Subscribed: {mid} {granted_qos}")

    # def on_log(self, client, userdata, level, buf):
    #     logging.info(f"Log: {buf}")

    def connect(self):
        self.client.username_pw_set(self.username, self.password)
        try:
            self.client.connect(self.host, self.port, 60)
        except ConnectionRefusedError:
            logging.error(
                f"Connection refused. Is the broker running at {self.host}:{self.port}?"
            )
            print(
                f"Connection refused. Is the broker running at {self.host}:{self.port}?"
            )
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            print(f"An error occurred: {e}")
        self.client.loop_start()
        logging.info(f"Connected to MQTT broker at {self.host}:{self.port}")

    def publish_message(
        self, topic: str, payload: str, qos: int = 0, retain: bool = False
    ) -> bool:
        if not self.client.is_connected():
            logging.error("Cannot publish message, MQTT client is not connected.")
            return False

        if not topic:
            logging.error("Cannot publish message, topic is empty.")
            return False

        if qos not in [0, 1, 2]:
            logging.warning(f"Invalid QoS value {qos} provided. Using QoS 0.")
            qos = 0

        try:
            logging.info(
                f"Publishing message to topic '{topic}' with QoS {qos}. Payload: '{payload}'"
            )
            msg_info = self.client.publish(topic, payload, qos=qos, retain=retain)

            if msg_info.rc == mqtt.MQTT_ERR_SUCCESS:
                logging.info(
                    f"Message (mid: {msg_info.mid}) accepted for publishing to topic '{topic}'."
                )
                return True
            else:
                logging.error(
                    f"Failed to publish message to topic '{topic}'. Publish rc: {msg_info.rc}"
                )
                return False
        except Exception as e:
            logging.error(
                f"Exception during MQTT publish to topic '{topic}': {e}",
                exc_info=True,
            )
            return False
