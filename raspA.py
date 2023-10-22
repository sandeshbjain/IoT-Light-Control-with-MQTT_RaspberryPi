import paho.mqtt.publish as publish
import RPi.GPIO as GPIO
import serial
import time
import datetime

import paho.mqtt.client as mqtt

ser = serial.Serial("/dev/ttyS0", 115200)

LDR_TOPIC = "lightSensor"
POT_TOPIC = "threshold"
MQTT_SERVER= "192.168.1.181"
initial_LDR_data=0
initial_POT_data=0
LED_PIN=18
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN,GPIO.OUT)


statusonline = "online"
statusoffline = "offline"

#minimum and maximum LDR and POT values
#EQUATION TO TURN ON LED FOR LDR: if Final_LDR > 2000+ (2095/4095)*final_POT => turn on GPIO

# Create an MQTT client instance
client = mqtt.Client(client_id="RaspberryPiA")

# Callback function when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
	#Publish the online status as a retained message
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        payload= f"{statusonline}|{timestamp}" 
        client.publish("Status/RaspberryPiA",payload, retain=True)
    else:
        print("Connection failed")

# Callback function when a message is received
def on_message(client, userdata, message):
    print("message C",message.topic)
			
# Set the callback functions
client.on_connect = on_connect
client.on_message = on_message

# Set up the last will message for the "Status/RaspberryPiA" topic
timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#payload= f"{statusoffline}|{timestamp}" 
last_will = f"Publisher disconnected|{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
client.will_set("Status/RaspberryPiA", last_will , retain=True)

# Connect to the MQTT broker
client.connect(MQTT_SERVER, 1883, keepalive=5)

# Start the MQTT client's loop (this will keep the client running and handling messages)
client.loop_start()

while True:
    # **********LDR data receive***************
    
    received_data_0 = ser.read()
    time.sleep(0.02)
    received_data_1 = ser.read()
    time.sleep(0.02)
    received_data_2 = ser.read()
    time.sleep(0.02)
    received_data_3 = ser.read()
    time.sleep(0.02)

    final_POT_data = 256*received_data_1[0] + received_data_0[0]
    # ******LDR calculations and publish*****
    final_LDR_data = received_data_3[0] * 256 + received_data_2[0]
    
    #print("Input Values = ",final_POT_data,final_LDR_data,"\n")
	
    try:
	
	    if ((abs(initial_LDR_data - final_LDR_data) >= 50) or (final_LDR_data - initial_LDR_data) >= 50 or (abs(initial_POT_data - final_POT_data) >= 100) or (final_POT_data - initial_POT_data) >= 100 ):
		    publish.single(LDR_TOPIC, final_LDR_data, hostname=MQTT_SERVER, qos=2)
		    publish.single(POT_TOPIC, final_POT_data, hostname=MQTT_SERVER, qos=2)			
		    print("Input Values = ",final_POT_data,final_LDR_data,"\n")
	
	    initial_LDR_data = final_LDR_data
	    initial_POT_data = final_POT_data
	
    except Exception as e:
	    print("Ungraceful Disconnect occured")
	    client.publish("Status/RaspberryPiA", last_will ,qos=2, retain=True)
	    break
