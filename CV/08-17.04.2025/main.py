import network
from time import sleep, time
import json
import machine
import random
import urequests
import gc

PERIOD = 10  # Perioda odesilani dat
last_temp = 23.5  # Pocatecni hodnota simulovanych dat

SENSOR_ID = "rpipw-01"
STUDENT_ID = "drmotada"

INFLUXDB_API_TOKEN = "5SHxtdKdvTKreWjlXh5ENhEG6Wb7U8cEmdWZG8mC2Y9670a6ax8Qx3EOOZ_MtuyqzPo4JpY1_ZKNLb_Z0_yawQ=="
INFLUXDB_SERVER = "mqtt.internal"
INFLUXDB_ORG = "NSI"
INFLUXDB_BUCKET = "data"
INFLUXDB_MEASUREMENT = "nsi_2025_3"

INTERNET_SSID = "13373-IoT-Lab"
INTERNET_PASSWORD = "FetMc5Un>2dYzEM"


def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(INTERNET_SSID, INTERNET_PASSWORD)
    while wlan.isconnected() == False:
        print("Waiting for WiFi connection...")
        sleep(1)
    print("Connected to WiFi:", wlan.ifconfig())
    return wlan


def send_data_to_influxdb(temperature):
    url = f"http://{INFLUXDB_SERVER}:8086/api/v2/write?org={INFLUXDB_ORG}&bucket={INFLUXDB_BUCKET}&precision=ns"
    headers = {
        "Authorization": f"Token {INFLUXDB_API_TOKEN}",
        "Content-Type": "text/plain; charset=utf-8",
        "Accept": "application/json",
    }
    data = f"{INFLUXDB_MEASUREMENT},sensor_id={SENSOR_ID},student_id={STUDENT_ID} temperature={temperature}"
    try:
        response = urequests.post(url, headers=headers, data=data)
        if response.status_code == 204:
            print("Data successfully sent to InfluxDB! T = ", temperature, " °C")
            gc.collect()
            return True
        else:
            print("Failed to send data to InfluxDB.")
    except Exception as e:
        print("Error sending data to InfluxDB:", e)
    return False


try:
    wlan = connect_to_wifi()
    while True:
        new_temp = last_temp + random.uniform(-0.5, 0.5)
        if new_temp < 15:
            new_temp = 15
        elif new_temp > 30:
            new_temp = 30
        last_temp = new_temp
        send_data_to_influxdb(new_temp)
        sleep(PERIOD)
except KeyboardInterrupt:
    machine.reset()
