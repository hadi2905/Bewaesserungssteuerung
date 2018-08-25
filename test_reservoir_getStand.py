import RPi.GPIO as GPIO
import reservoir as res
import time
import logging

try:
    GPIO.setmode(GPIO.BOARD)
    w = res.Reservoir(18,0,1,2,15)
  
#    w.pumpe("on")
#    time.sleep(10)
#    w.pumpe("off")
#    time.sleep(10)
#    w.pumpe("on")
#    time.sleep(10)
#    w.pumpe("off")
 
    while True:
        print("{:}  Wasserstand => {:}".format(time.strftime("%Y%m%d_%H%M%S"), w.gibStand()))
        time.sleep(2)

# Programm beenden
except KeyboardInterrupt:
    logger.exception("Programm abgebrochen")

#except:  
    # this catches ALL other exceptions including errors.  
    # You won't get any error messages for debugging  
    # so only use it once your code is working  
    #print ("Other error or exception occurred!"  )
  
finally:  
    GPIO.cleanup() # this ensures a clean exit  
