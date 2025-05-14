import simple
import do_connect
import time
import gc
from DHTsensor import read

do_connect.do_connect()

client = simple.MQTTClient(
    client_id="RaspberryPiPico", server="mqtt.internal", port=1883
)
client.connect()

temperature, humidity = read()

client.publish(topic="public/test", msg=(str(temperature), str(humidity)))


def my_callback(topic, msg):
    print("Message received:", topic, msg)


client.set_callback(my_callback)
client.subscribe("#")


while True:
    client.check_msg()
    time.sleep(1)
    gc.collect()
