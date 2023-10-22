import paho.mqtt.publish as publish
import RPi.GPIO as GPIO
import serial
import time
import datetime

import paho.mqtt.client as mqtt

MQTT_SERVER= "192.168.1.181"
initial_LDR_data=0
initial_POT_data=0




statusonline = "online"
statusoffline = "offline"

#minimum and maximum LDR and POT values
#EQUATION TO TURN ON LED FOR LDR: if Final_LDR > 2000+ (2095/4095)*final_POT => turn on GPIO

# Create an MQTT client instance
client = mqtt.Client(client_id="RaspberryPiC")

# Callback function when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
	#Publish the online status as a retained message
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        payload= f"{statusonline}|{timestamp}" 
        client.publish("Status/RaspberryPiC",payload, retain=True)
        client.subscribe("lightSensor")
        client.subscribe("threshold")
    else:
        print("Connection failed")

prev_status = "0"
# Callback function when a message is received
def on_message(client, userdata, message):
    global LDR_DATA, POT_data, prev_status
    if message.topic == "lightSensor":
        LDR_DATA = message.payload.decode("utf-8")
    if message.topic == "threshold":
        POT_data=message.payload.decode("utf-8")
        print("LDR_data=",LDR_DATA, "pot data", POT_data)
        current_status = "1" if(float(LDR_DATA)>(2000+0.511*float(POT_data))) else "0"
            
        #publish the current status if it has changed
        if current_status != prev_status:
            client.publish("LIGHTstatus",payload=current_status,retain=True,qos=2)
            prev_status = current_status
       
# Set the callback functions
client.on_connect = on_connect
client.on_message = on_message

# Set up the last will message for the "Status/RaspberryPiA" topic
timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#payload= f"{statusoffline}|{timestamp}" 
last_will = f"Raspberry C Offline disconnected|{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
client.will_set("Status/RaspberryPiC", last_will , retain=True)

# Connect to the MQTT broker
client.connect(MQTT_SERVER, 1883, keepalive=5)
client.on_connect = on_connect
client.on_message = on_message
# Start the MQTT client's loop (this will keep the client running and handling messages)

client.on_connect = on_connect
client.on_message = on_message

# Set up the last will message for the "Status/RaspberryPiC" topic
timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#payload= f"{statusoffline}|{timestamp}" 
last_will = f"Publisher disconnected|{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
client.will_set("Status/RaspberryPiC", last_will , retain=True)

# Connect to the MQTT broker
client.connect(MQTT_SERVER, 1883, keepalive=5)

# Start the MQTT client's loop (this will keep the client running and handling messages)
client.loop_forever()

    
