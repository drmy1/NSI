import queue
from mqtt import Mqtt

message_queue = queue.Queue()  # type: ignore
mqtt_client_handler = Mqtt()
