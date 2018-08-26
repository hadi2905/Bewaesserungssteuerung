import RPi.GPIO as GPIO
import reservoir as res
import time
import logging

try:
    logger=logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter=logging.Formatter('%(asctime)s | %(levelname)s -> %(message)s')
    # creating a handler to log on the filesystem
    file_handler=logging.FileHandler('/home/pi/test_reservoir.log')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    # adding handlers to our logger
    logger.addHandler(file_handler)
    #creating a handler to log on the console
    stream_handler=logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler)
    GPIO.setmode(GPIO.BOARD)
    r = res.Reservoir(18,0,1,2,16)
    ret = r.fuelleBisLevel(2)
    logger.info("Rückgabe: {:}".format(ret))
    
#    while True:
#        print("{:}  Wasserstand => {:}".format(time.strftime("%Y%m%d_%H%M%S"), w.gibStand()))
#        time.sleep(2)

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
