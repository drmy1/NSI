import paho.mqtt.publish as publish

publish.single("NSI_2025/test", "nsssazdar!", hostname="mqtt.eclipseprojects.io", qos=2)
