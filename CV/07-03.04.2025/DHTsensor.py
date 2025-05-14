import machine
import dht

d = dht.DHT22(machine.Pin(0))


def read():
    try:
        d.measure()
        temperature = d.temperature()
        humidity = d.humidity()
        return temperature, humidity
    except:
        d.measure()
