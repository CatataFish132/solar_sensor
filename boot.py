import network, esp, gc, BME280, ujson, time, ntptime, urequests, utime
import socket
from time import sleep
from machine import Pin, I2C, ADC, Timer, RTC

esp.osdebug(None)
gc.collect()

# read config file
with open("config.json", "r") as f:
  config = ujson.loads(f.read())

# setup i2c
i2c = I2C(0)

# connect to the wlan
station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(config["ssid"], config["password"])

while station.isconnected() == False:
  pass

print('Connection successful')
print(station.ifconfig())

# set date and time
url = "https://worldtimeapi.org/api/timezone/Europe/Amsterdam"

response = urequests.get(url)

if response.status_code == 200:
  parsed = response.json()
  datetime_str = str(parsed["datetime"])
  year = int(datetime_str[0:4])
  month = int(datetime_str[5:7])
  day = int(datetime_str[8:10])
  hour = int(datetime_str[11:13])
  minute = int(datetime_str[14:16])
  second = int(datetime_str[17:19])
  subsecond = int(round(int(datetime_str[20:26]) / 10000))
  rtc = RTC()
        
  # update internal RTC
  rtc.datetime((year, month, day, 0, hour, minute, second, subsecond))

# this always crashed the second time
# ntptime.host = "1.europe.pool.ntp.org"
# ntptime.settime()
# print(time.localtime())