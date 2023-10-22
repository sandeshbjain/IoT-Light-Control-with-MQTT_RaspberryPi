import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time
import datetime

GPIO_PIN1 = 18
GPIO_PIN14 = 14
GPIO_PIN15 = 15
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN1,GPIO.OUT)
GPIO.setup(GPIO_PIN14,GPIO.OUT)
GPIO.setup(GPIO_PIN15,GPIO.OUT)

GPIO.output(GPIO_PIN1, GPIO.LOW)
GPIO.output(GPIO_PIN14,GPIO.LOW)
GPIO.output(GPIO_PIN15,GPIO.LOW)

client = mqtt.Client()

timestamp =datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
online = "online"

def on_connect(client, userdata, flags, rc):
    print("Connected to the broker for LDR1 data")
    client.subscribe("Status/RaspberryPiA")
    client.subscribe("Status/RaspberryPiC")
    client.subscribe("LIGHTstatus")
    client.publish("Status/RaspberryPiB", payload= f"{online} | {timestamp}", retain = True)
    

    
def on_message(client,userdata, message):
    global LDR_data, POT_data
    if message.topic == "LIGHTstatus":
        print("LIGHT status=",message.payload.decode("utf-8"))
        if (message.payload.decode("utf-8") == "1"):
            GPIO.output(GPIO_PIN14,GPIO.HIGH)
            print("LED 14 HIGH")
        else:
            GPIO.output(GPIO_PIN14,GPIO.LOW)
            print("LED 14 LOW")    
                    
    elif message.topic == "Status/RaspberryPiA":
        payload=message.payload.decode("utf-8")
        status,timestamp=payload.split("|")
        print(status)
        if status == "online":
            GPIO.output(GPIO_PIN1, GPIO.HIGH)
            print("Raspberry Pi A is Online")
        else:
            GPIO.output(GPIO_PIN1, GPIO.LOW)
            print("Raspberry Pi A is Offline")
            
    elif message.topic == "Status/RaspberryPiC":
        payload=message.payload.decode("utf-8")
        status,timestamp=payload.split("|")
        print(status)
        if status == "online":
            GPIO.output(GPIO_PIN15, GPIO.HIGH)
            print("Raspberry Pi C is Online")
        else:
            GPIO.output(GPIO_PIN15, GPIO.LOW)
            print("Raspberry Pi C is Offline")
            GPIO.output(GPIO_PIN14,GPIO.LOW)

        
client.on_connect = on_connect
client.on_message = on_message
client.will_set("Status/RaspberryPiB", payload="offline", retain=True)

client.connect("192.168.1.181", 1883)
client.loop_forever()

try:
    pass
except KeyboardInterrupt:
    GPIO.cleanup()
finally:
    GPIO.cleanup()
