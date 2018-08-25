# -*- coding: utf-8 -*-
"""

 
      
"""
import time
import datetime as dt
import logging
import os 
import json
import subprocess as sp


from RPi import GPIO
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import Adafruit_DHT as ada
import SDL_DS3231 as rtc
import rtc_tools as rt
import reservoir as rv
import bewaesserung_lib as lib
import bewaesserung_rlib as rlib 
from pathlib import Path

home = str(Path.home())

MIN_DELAY_SHUTDOWN = 5
ZIELLEVEL = 3       # Ziellevel für Befüllung des Reservoirs

# Logger initialisieren
logger = logging.getLogger()
logger.setLevel(logging.INFO)

fH = logging.FileHandler(home + '/test_bewaesserung_rlib.log')
fH.setLevel(logging.INFO)

cH = logging.StreamHandler()
cH.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fH.setFormatter(formatter)
cH.setFormatter(formatter)

logger.addHandler(fH)
logger.addHandler(cH)

#################################################################################################################################################

    
mcp = rlib.get_mcp()
rtClock = rlib.get_rtClock()


# Konfigurationsdaten und Messwerte aus Dateien lesen
cfgData = lib.read_json_cfg()
data = lib.read_json_data(cfgData)

print("Hotspot ",rlib.check_hotspot("MOBSPOT"))
rlib.set_gpio_settings()
#print(rlib.temp_und_luftfeuchtigkeit_messen())

rlib.sensordaten_auslesen(rtClock, mcp, data)
print(data)

# Jetzt noch die Daten speichern und RTC auf nächsten Startzeitpunkt programmieren
#lib.save_json(cfgData, data)

u_bat=rlib.batteriespannung_messen(mcp)
print("u_bat=",u_bat)
x = rlib.temp_und_luftfeuchtigkeit_messen()
print(x)

GPIO.cleanup()
