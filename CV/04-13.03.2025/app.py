import queue
import json
# import paho.mqtt.subscribe as subscribe

from flask import Flask, Response, render_template
from flask_mqtt import Mqtt

q = queue.Queue()
output = dict()

app = Flask(__name__)
app.config["MQTT_BROKER_URL"] = "mqtt.eclipseprojects.io"
app.config["MQTT_BROKER_PORT"] = 1883
mqtt = Mqtt(app)


@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe("nsi/#")


@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(topic=message.topic, payload=message.payload.decode())
    print("topic:{}, payload: {}".format(message.topic, message.payload.decode()))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=True)
