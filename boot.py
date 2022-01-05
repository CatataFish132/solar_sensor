import network, esp, gc, BME280, ujson
import usocket as socket
from time import sleep
from machine import Pin, I2C

esp.osdebug(None)
gc.collect()

# read config file
with open("config.json", "r") as f:
  config = ujson.loads(f.read())

i2c = I2C(0)

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(config["ssid"], config["password"])

while station.isconnected() == False:
  pass

print('Connection successful')
print(station.ifconfig())