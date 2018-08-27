# -*- coding: utf-8 -*-
"""
Testskript zum Messen der Bodenfeuchtigkeit
Ausgabe der beiden Messwerte erfolgt auf dem Bildschirm     
"""
from RPi import GPIO
import bewaesserung_lib as lib
import bewaesserung_rlib as rlib 

rlib.set_gpio_settings()
mcp = rlib.get_mcp()
print(rlib.bodenfeuchtigkeit_messen(mcp))    
GPIO.cleanup()



