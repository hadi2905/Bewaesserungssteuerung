import subprocess as sp
import time
import datetime as dt
import logging


from RPi import GPIO
import Adafruit_DHT as ada
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import SDL_DS3231 as rtc

import rtc_tools as rt
import luftfeuchtigkeit as luf



# Hardware SPI configuration:
SPI_PORT   = 0
SPI_DEVICE = 0
PIN_DHT22 = 4
PIN_DELAY_SHUTDOWN = 40
PIN_VCC_MESS = 18

MCP_KANAL_BODEN1 = 4
MCP_KANAL_BODEN2 = 5
MCP_KANAL_BAT = 7

MIN_NAECHST_START = 60


logger = logging.getLogger()

def set_gpio_settings():
    """
    Initialisiert die GPIO-Einstellungen des Raspi
    """
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(PIN_VCC_MESS, GPIO.OUT)                                  # Messspannung für Bodenhygrometer steuern
    GPIO.setup(PIN_DELAY_SHUTDOWN, GPIO.IN, pull_up_down=GPIO.PUD_UP)   # Wenn Pin auf Ground liegt wird Shutdown verzögert. Default ist Pullup
    


def temp_und_luftfeuchtigkeit_messen():
    sensor = ada.DHT22

    # Da beim Auslesen die letzte Messung, die schon einige Zeit zurückliegen kann, abgerufen wird, fragen wir 2 mal in kurzem Abstand
    # Achtung: Die DHT22-Bibliothek scheint sich nicht darum zu scheren ob setmode mit BOARD oder BCM aufgerufen wurde. Sie verwendet die 
    # übergebene PIN-Nummer im Sinne von BCM. D.h. PIN_DHT22=4 wird interpretiert als Pin GPIO4 und nicht Pin 7 auf dem Board
    h, t = ada.read(sensor, PIN_DHT22)
    time.sleep(6)
    h, t = ada.read(sensor, PIN_DHT22)
    n = 0
    while (not h or not t) and n < 3:       # Wenn kein Messwert vorliegt, versuchen wir es noch 3 mal
        time.sleep(6)
        h, t = ada.read(sensor, PIN_DHT22)
        n = n +1
            
    if not h or not t:
        logger.error("Messung fehlgeschlagen")
        return(None, None, None)
    else:
        h_abs = 1000*luf.abs_feuchte(t,h);   # Absolute Luftfeuchtigkeit wird auf Temperatur und rel. Feuchte errechnet
        logger.debug('Temperatur: {0:0.1f}*C rel.Luftfeuchtigkeit: {1:0.1f}% abs.Luftfeuchtigkeit: {2:0.3f} g/m³'.format(t, h, h_abs))
        return (round(t,1), round(h, 1), round(h_abs, 1))
            
def bodenfeuchtigkeit_messen(mcp):
    GPIO.output(PIN_VCC_MESS, 1)
    time.sleep(0.5)
    v1 = mcp.read_adc(MCP_KANAL_BODEN1)
    v2 = mcp.read_adc(MCP_KANAL_BODEN2)
    logger.debug("Bodenfeuchtigkeit M1:{:}  M2:{:}".format(v1,v2))
    GPIO.output(PIN_VCC_MESS,0)
    return (v1,v2)

def batteriespannung_messen(mcp):
    # Die Autobatterie wird über einen Spannungsteiler an Kanal 7 gemessen
    time.sleep(0.5)
    u = float(mcp.read_adc(MCP_KANAL_BAT)/20)
    logger.debug("1. Messung u_bat={}".format(u)) 
    time.sleep(0.5)
    # aus irgendeinem Grund weicht die erste Messung immer etwas ab
    u = float(mcp.read_adc(MCP_KANAL_BAT)/20)
    logger.debug("2. Messung u_bat={}".format(u)) 
    return (u)
    
    
def sensordaten_auslesen(rtClock, mcp, data):
    logger.info("Sensoren auslesen")
    u_bat=batteriespannung_messen(mcp)
    klima = temp_und_luftfeuchtigkeit_messen()
    bd = bodenfeuchtigkeit_messen(mcp)
    u_bat=batteriespannung_messen(mcp)
    data.append([dt.datetime.now().isoformat(), u_bat, klima, bd])
   
def sensordaten_auslesen2():
    """
    Diese Funktion kann genutzt werden um die Sensoren abzurufen wenn das Modul bewaesserung.py per import in eine Python-Session eingebunden wird
    """
    data = []
    set_gpio_settings()
    sensordaten_auslesen(get_rtClock(), get_mcp(), data)
    print(data)
    
"""    
def naechsten_start_bestimmen(rtClock):    
    # Den Alarm fortschreiben
    # Tag, Stunde und Minute des letzten Alarms aus RTC Registern lesen
    d = rtClock.read_datetime().date()
    m = rtc.bcd_to_int(rtClock._read(8)&127)
    h = rtc.bcd_to_int(rtClock._read(9)&127)
    letzterAlarm = dt.datetime.combine(d, dt.time(h,m,0))
    logger.debug("Letzte Startzeit laut RTC-Register {:}".format(letzterAlarm))
    if letzterAlarm < rtClock.read_datetime() - dt.timedelta(minutes=3):      # wenn der letzte Alarm nicht "gerade eben" (vor dem letzten Raspi-Start) war...
        naechsterAlarm = rtClock.read_datetime() + dt.timedelta(minutes=MIN_NAECHST_START)    # ... dann setzen wir das Intervall auf die aktuelle Zeitpunkt
    elif letzterAlarm < rtClock.read_datetime() + dt.timedelta(minutes=1): 	# Der letzte Alarm war vor kurzem (=Normalfall) oder steht kurz bevor
        naechsterAlarm = letzterAlarm + dt.timedelta(minutes=MIN_NAECHST_START)
    else:                                                               # Dritte Möglichkeit: der Alarm ist in der Zukunft.
        if letzterAlarm > rtClock.read_datetime() + dt.timedelta(minutes=MIN_NAECHST_START):	# Letzter Alarm ist weiter in der Zukunft als Jetzt + Intervall
            naechsterAlarm = rtClock.read_datetime() + dt.timedelta(minutes=MIN_NAECHST_START)
        else:
            naechsterAlarm = None

    if naechsterAlarm:
        rt.set_alarm1_datetime(rtClock, naechsterAlarm)
        logger.info("Naechste Startzeit {:}".format(naechsterAlarm))
    else:
        logger.info("Keine Aenderung der naechsten Startzeit")
"""

def naechsten_start_bestimmen(rtClock):
    #
    # Der nächste Startzeitpunkt wird mit Hilfe des Dictionary crontab bestimmt. Die aktuelle Stunde wird als Key genommen um die Stunde für den 
    # nächsten Start zu bestimmen
    #
    crontab = {0:1,1:3,2:3,3:5,4:5,5:7,6:7,7:9,8:9,9:11,10:11,11:13,12:13,13:15,14:15,15:17,16:17,17:19,18:19,19:21,20:21,21:23,22:23,23:1}
    
    d = rtClock.read_datetime()
    nextHour = crontab[d.hour]
    naechsterAlarm = dt.datetime.combine(d.date(), dt.time(nextHour,0,0))
    
    if nextHour<d.hour:     # Tageswechsel feststellen
        naechsterAlarm = naechsterAlarm+dt.timedelta(days=1)
        
    rt.set_alarm1_datetime(rtClock, naechsterAlarm)
    logger.info("Naechste Startzeit {:}".format(naechsterAlarm))
    
 
def json_einlesen(data):
    for i in range(len(data)):
        zeit = dt.datetime.strptime(data[i][0], "%Y-%m-%dT%H:%M:%S.%f")
        wert = data[i][3]
        print("Zeit {:}   Wert {:}".format(zeit, wert))


def check_hotspot(spotName):
    """
    Prüft ob der Raspi mit dem Hotspot 'MOBSPOT' verbunden ist
    In diesem Fall findet sich der Name des Hotspot im vierten Listenelement der Rückgabe von iwconfig: b'ESSID:"MOBSPOT"'
    Falls keine WLAN-Verbindung existiert, steht da b'ESSID:off/any'
    """
    pr = sp.run(["sudo","iwconfig"], stdout=sp.PIPE, stderr=sp.DEVNULL)
    for i in range(6):
        logger.debug("Ergebnis iwconfig Zeile {:}: {:}".format(i,str(pr.stdout.split()[i])))
    essid = str(pr.stdout.split()[3])
    if essid.find(spotName)>=0:
        return True
    else:
        return False

def get_mcp():
    """
    Instanziiert ein MCP-Objekt (Analog-Digital-Konverter)
    """
    return Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))
    
def get_rtClock():
    """
    Instanziiert ein Real Time Clock Objekt
    """
    return rtc.SDL_DS3231()


