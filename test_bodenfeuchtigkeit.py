# -*- coding: utf-8 -*-
"""

 
      
"""
from RPi import GPIO
import bewaesserung_lib as lib
import bewaesserung_rlib as rlib 

rlib.set_gpio_settings()
mcp = rlib.get_mcp()
print(rlib.bodenfeuchtigkeit_messen(mcp))    
GPIO.cleanup()


 # Modul sys wird importiert:
import sys                

# Iteration über sämtliche Argumente:
for eachArg in sys.argv:   
        print (eachArg)
        
if len(sys.argv)>1 and sys.argv[1]=="ignore":
    print("OK")
else:
    print("NOK")
