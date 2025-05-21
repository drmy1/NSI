import paho.mqtt.client as mqtt  # type: ignore
import logging
import os
from extensions import is_valid_ipv4
from dotenv import load_dotenv


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

    def __init__(self):
        self.client = mqtt.Client(clean_session=True, client_id="NSI_semestralka")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_publish = self.on_publish
        self.client.on_subscribe = self.on_subscribe
        self.client.on_log = self.on_log
        env_settings = Env()
        self.username = env_settings.getuser
        self.password = env_settings.getpassword
        self.host = env_settings.gethost
        self.port = env_settings.getport
        self.topics_to_subscribe = [("#", 0)]

    @classmethod
    def setsub(cls) -> None:
        logging.info("Setting subscription to True")
        cls.subscribed = True

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logging.info(f"Subscribing to topics: {self.topics_to_subscribe}")
            client.subscribe(self.topics_to_subscribe)
            print(f"Connected with result code {rc}")

        else:
            logging.error(f"Connection failed, not subscribing. Result code: {rc}")
        logging.info(f"Connected with result code {rc}")

    def on_message(self, client, userdata, msg):
        match self.subscribed:
            case True:
                logging.info(f"Message received: {msg.topic} {msg.payload.decode()}")
                print(f"Message received: {msg.topic} {msg.payload.decode()}")
            case False:
                logging.info("Program started configuting subscription...")
                self.setsub()

    def on_publish(self, client, userdata, mid):
        logging.info(f"Message published: {mid}")
        print(f"Message published: {mid}")

    def on_subscribe(self, client, userdata, mid, granted_qos):
        logging.info(f"Subscribed: {mid} {granted_qos}")
        print(f"Subscribed: {mid} {granted_qos}")

    def on_log(self, client, userdata, level, buf):
        logging.info(f"Log: {buf}")

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
        finally:
            logging.info("Cleaning up and exiting.")
            print("Cleaning up and exiting.")
        self.client.loop_start()
        logging.info(f"Connected to MQTT broker at {self.host}:{self.port}")
        print(f"Connected to MQTT broker at {self.host}:{self.port}")
