#import ssd1306
from hcsr04 import HCSR04
from umqttsimple import MQTTClient
from machine import Pin,PWM
import time
import ubinascii
import machine
import micropython
import network
import esp

import gc
from config import *

esp.osdebug(None)
gc.collect()

mqtt_server = '192.168.17.5'
topic_sub = b'Motion/EntryMotion/STATE'
topic_pub = b'Doorbell/STATE'


motionFlag = 0
motionLedDuration = 10

ledWhite = machine.Pin(5, machine.Pin.OUT)

doorbellFlag = 0
blinkCounter = 3
distanceLimit = 400

sensor = HCSR04(trigger_pin=13, echo_pin=12,echo_timeout_us=1000000)

wlan=network.WLAN(network.STA_IF)

#====================================
def connectWiFi(ID,password):
  i=0
  wlan.active(True)
  wlan.disconnect()
  wlan.connect(ID, password)
  while(wlan.ifconfig()[0]=='0.0.0.0'):
    i = i + 1
    time.sleep(1)
    if (i > 20):
      break
  return True

#====================================
def sub_cb(topic, msg):
  global motionFlag
  print('sub rcv:')
  print((topic, msg))
  motionFlag = motionLedDuration

#====================================
def connect_and_subscribe():
  global client_id, mqtt_server, topic_sub
  client = MQTTClient(client_id, mqtt_server)
  client.set_callback(sub_cb)
  client.connect()
  client.subscribe(topic_sub)
  print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub))
  return client

#====================================
def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(10)
  machine.reset()

#====================================
def processMotionLed():
  global motionFlag 
  print('led delay = {0}'.format(motionFlag)) 
  if (motionFlag > 0):
    if (motionFlag == motionLedDuration):
      ledWhite.value(1)
      print('led ON = {0}'.format(motionFlag))
    elif (motionFlag == 1):
      ledWhite.value(0)      
      print('led OFF = {0}'.format(motionFlag))

    if (motionFlag > 0):
      motionFlag = motionFlag - 1


#====================================
def processDoorbell():
  global motionFlag , doorbellFlag
  doorbellFlag = 1
  print('<<DoorBell>>')
  client.publish(topic_pub, str(distance))
  motionFlag = 0
  ledWhite.value(0)
  i = 0
  while i < blinkCounter:
    ledWhite.value(1)
    time.sleep(0.6)
    ledWhite.value(0)
    time.sleep(0.3)
    i = i + 1
  doorbellFlag = 0
#=====Starting point===============================
print("Start Execution\n") 
connectWiFi(SSID,PSW)
client_id = ubinascii.hexlify(machine.unique_id())

if not wlan.isconnected():
  print('connecting to network...' + SSID)
  connectWiFi(SSID, PSW)
  time.sleep(2)
print("Wifi connected\n") 
try:
  client = connect_and_subscribe()
  print("MQTT connected\n") 
except OSError as e:
  print("MQTT error\n") 
  restart_and_reconnect()

while True:
  try:
    client.check_msg()
    #if (time.time() - last_message) > message_interval:
    distance = sensor.distance_mm()
    
    if (distance > 0 and distance < distanceLimit and doorbellFlag == 0):
      processDoorbell()

    print('distance = {0}'.format(distance)) 
    processMotionLed()

      #last_message = time.time()
      #counter += 1
    time.sleep(1)

  except OSError as e:
    restart_and_reconnect()


