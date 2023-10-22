import paho.mqtt.client as mqtt
import logging
import datetime

# Create two logger instances for different log files
all_status_logger = logging.getLogger("All_Status")
light_status_logger = logging.getLogger("Light_Status")

# Configure the loggers to write to different log files
all_status_handler = logging.FileHandler("All_Status_log.txt")
light_status_handler = logging.FileHandler("Light_Status_log.txt")

# Set the log level for both loggers
all_status_logger.setLevel(logging.INFO)
light_status_logger.setLevel(logging.INFO)

# Create a formatter to include timestamp in the log messages
formatter = logging.Formatter('%(message)s %(asctime)s')

# Set the formatter for the log handlers
all_status_handler.setFormatter(formatter)
light_status_handler.setFormatter(formatter)

# Add the handlers to the loggers
all_status_logger.addHandler(all_status_handler)
light_status_logger.addHandler(light_status_handler)

client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print("Connected to the broker for lightSensor, threshold, Status/RaspberryPiA, and Status/RaspberryPiC data")
    client.subscribe("lightSensor", qos=2)
    client.subscribe("threshold", qos=2)
    client.subscribe("LIGHTstatus", qos=2)
    client.subscribe("Status/RaspberryPiA", qos=2)
    client.subscribe("Status/RaspberryPiC", qos=2)

def on_message(client, userdata, message):
    global LDR_DATA, POT_data

    if message.topic == "lightSensor":
        LDR_DATA = message.payload.decode("utf-8")
        all_status_logger.info(f"lightSensor data: {LDR_DATA} {datetime.datetime.now()}")

    if message.topic == "threshold":
        POT_data = message.payload.decode("utf-8")
        all_status_logger.info(f"Threshold data: {POT_data} {datetime.datetime.now()}")

    if message.topic == "LIGHTstatus":
        print("LIGHT status =", message.payload.decode("utf-8"))
        if message.payload.decode("utf-8") == "1":
            light_status_logger.info(f"LIGHTstatus HIGH {datetime.datetime.now()}")
        else:
            light_status_logger.info(f"LIGHTstatus LOW {datetime.datetime.now()}")

    elif message.topic == "Status/RaspberryPiA":
        payload = message.payload.decode("utf-8")
        status, timestamp = payload.split("|")
        print(status)
        if status == "online":
            all_status_logger.info(f"Raspberry Pi A is Online {datetime.datetime.now()}")
        else:
            all_status_logger.info(f"Raspberry Pi A is Offline {datetime.datetime.now()}")

    elif message.topic == "Status/RaspberryPiC":
        payload = message.payload.decode("utf-8")
        status, timestamp = payload.split("|")
        print(status)
        if status == "online":
            all_status_logger.info(f"Raspberry Pi C is Online {datetime.datetime.now()}")
        else:
            all_status_logger.info(f"Raspberry Pi C is Offline {datetime.datetime.now()}")

client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.1.181", 1883)
client.loop_forever()
