from common import *
from lcd import LCD
import time
from machine import I2C, Pin

# Update pin numbers as needed
i2c = I2C(0, sda=Pin(16), scl=Pin(17), freq=400000)
lcd = LCD(i2c)
lcd.message("System Startup.")
time.sleep(2)

# Do something if PIN does not exist

# Normal operation loop
while True:
    pass