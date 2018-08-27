# -*- coding: utf-8 -*-
"""
Zentrales Skript für die Bewässerungssteuerung mit den Funktionen
    main()
    bewaesserungsablauf()
    shutdown()

main() führt Initialisierungen durch und entscheidet ob der normale Bewässerungsablauf ausgeführt werden soll oder in den Wartungsmodus verzweigt wird

Der bewaesserungsablauf() führt die Messungen durch und speichert die Werte in der JSON-Datenstruktur. Dann prüft er ob die Voraussetzungen für eine Bewässerung vorliegen und startet ggf. die Bewässerungsroutine. Schließlich wird noch die JSON-Datenstruktur sowie die Konfigurationsdatei gespeichert und der nächste Startzeitpunkt bestimmt und in die RTC geschrieben

shutdown() setzt den Alarmausgang SQW der Realtime Clock zurück (damit beginnt die Entladung des Kondensators, was zum Abschalten der Versorgungsspannung führt) und startet den Shutdown des Raspi
"""
import time
import datetime as dt
import logging
import os 
import sys
import subprocess as sp


from RPi import GPIO
import rtc_tools as rt
import reservoir as res
import bewaesserung_lib as lib
import bewaesserung_rlib as rlib 

MIN_DELAY_SHUTDOWN = 5
ZIELLEVEL = 2       # Ziellevel für Befüllung des Reservoirs
MOBILER_HOTSPOT = "MOBSPOT"


# Logger initialisieren
logger = logging.getLogger()
logger.setLevel(logging.INFO)

fH = logging.FileHandler("/home/pi/bewaesserung.log")
fH.setLevel(logging.INFO)

cH = logging.StreamHandler()
cH.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fH.setFormatter(formatter)
cH.setFormatter(formatter)

logger.addHandler(fH)
logger.addHandler(cH)

#################################################################################################################################################

def shutdown():
    """
    Setzt den Alarmausgang SQW der Realtime Clock zurück (damit beginnt die Entladung des Kondensators, was zum Abschalten der Versorgungsspannung führt) und startet den Shutdown des Raspi

    Parameter
        keine
    """
    GPIO.cleanup()
    logger.info("Shutdown beginnt")
    # Der Reset muss unmittelbar vor dem Shutdown kommen da hiermit der RTC-Ausgang SQW wieder auf 1 geht
    rt.reset_alarm1_indicator(rlib.get_rtClock())   
    os.system("sudo shutdown now")


def bewaesserungsablauf(rtClock, mcp, cfgData, data, dt):
    """
    Führt die Messungen durch und speichert die Werte in der JSON-Datenstruktur. Dann prüft er ob die Voraussetzungen für eine Bewässerung vorliegen und startet ggf. die Bewässerungsroutine. Schließlich wird noch die JSON-Datenstruktur sowie die Konfigurationsdatei gespeichert und der nächste Startzeitpunkt bestimmt und in die RTC geschrieben
    
    Parameter
        rtClock:    Instanz des RTC-Objekts
        mcp:        Instanz des MCP3008-Objekts (Analog-Digital-Konverter)
        data:       JSON-Datenobjekt
        dt:         Datum-Uhrzeit-Objekt mit dem Timestamp des Starts
    """
    rlib.sensordaten_auslesen(rtClock, mcp, data)
    # Bewässerungslogik startet
    if cfgData['Bewaesserung_aktiv']:
        if dt.hour in cfgData['Bewaesserungsstunden']:
            bf = rlib.bodenfeuchtigkeit_messen(mcp)
            if bf[0] > cfgData['Grenzwert_Bodenfeuchtigkeit']:
                if cfgData['Anzahl_kein_Wasser'] <= 2:
                    logger.info("Bewässerung kann starten")
                    r = res.Reservoir(18,0,1,2,15)
                    ret = r.fuelleBisLevel(ZIELLEVEL)
                    if ret==ZIELLEVEL:
                        logger.info("Reservoir konnte auf Ziellevel {:} gefüllt werden".format(ZIELLEVEL))
                        cfgData['Anzahl_kein_Wasser'] = 0
                    else:
                        logger.info("Füllung Reservoir nur bis Level {:} statt {:} möglich".format(ret, ZIELLEVEL))
                        cfgData['Anzahl_kein_Wasser'] = cfgData['Anzahl_kein_Wasser'] + 1
                    logger.info("Wert von Anzahl_kein_Wasser: {:}".format(cfgData['Anzahl_kein_Wasser']))
                else:
                    logger.info("Abbruch da bei den letzten beiden Versuchen kein Wasser verfügbar war")
            else:
                logger.info("Abbruch Bodensensor zeigt genügend Feuchtigkeit an ({:}/Grenzwert {:})".format(bf[0], cfgData['Grenzwert_Bodenfeuchtigkeit']))
        else:
            logger.info("keine Uhrzeit für Bewässerung")
    else:
        logger.info("Bewässerung ist nicht aktiviert")
        
    # Jetzt noch die Daten speichern und RTC auf nächsten Startzeitpunkt programmieren
    lib.save_json(cfgData, data)
    rlib.naechsten_start_bestimmen(rtClock)
    
    
def main():
    """
    Initialisiert die Verbindngen zur RTC und den angeschlossenen Sensoren
    Prüft ob die Verzögerungs-Pin auf Masse legt bzw. ein bekannter Hotspot erreichbar ist.
    Falls ja, wird in den Wartungsmodus verzweigt und der Shutdown um 5 Minuten verzögert, andernfalls wird der normale Zyklus ausgeführt 
    
    Parameter
        keine
    """
    try:
        # Den Analog-Digital-Konverter MCP3008 und die RTC und initialisieren
        mcp = rlib.get_mcp()
        rtClock = rlib.get_rtClock()
        
        # Die Raspi-Uhr nach dem Booten mit Date/Time der RTC versorgen
        dt = rtClock.read_datetime()
        sp.run(["sudo", "date", "--set", dt.strftime("%Y-%m-%d %H:%M:%S")])

        logger.info("Starte Main")

        # Konfigurationsdaten und Messwerte aus Dateien lesen
        cfgData = lib.read_json_cfg()
        data = lib.read_json_data(cfgData)

        rlib.set_gpio_settings()
        
        # Prüfen ob Pin PIN_DELAY_SHUTDOWN auf 0 liegt
        delayPin = GPIO.input(rlib.PIN_DELAY_SHUTDOWN)
        logger.info("Prüfung Pin {:},  Ergebnis: {:}".format(rlib.PIN_DELAY_SHUTDOWN, delayPin))
        hotspot_found = rlib.check_hotspot(MOBILER_HOTSPOT)
        logger.info("Prüfung auf Hotspot " + MOBILER_HOTSPOT + ". Ergebnis: {:}".format(hotspot_found))
        # Falls der Hotspot des Smartphones empfangen wird oder der delayPin auf 0 liegt
        # wollen wir uns mit dem Raspi verbinden und nicht dass er sein übliches Programm fährt
        if (delayPin==0 or hotspot_found) and not (len(sys.argv)>1 and sys.argv[1]=="ignore"):   # mit dem Kommandozeileargument "ignore" kann der normale Ablauf erzwungen werden auch wenn der Hotspot gefunden wurde
            logger.info("Breche Programm ab, Shutdown verzoegert da mit mobilem Hotspot " + MOBILER_HOTSPOT + " verbunden oder DelayPin auf 0")
        else:    
            logger.info("Starte Bewässerungsablauf")
            bewaesserungsablauf(rtClock, mcp, cfgData, data, dt)

        # Shutdown um x min verzögern falls Pin PIN_DELAY_SHUTDOWN auf Masse liegt (Default ist Pullup) 
        # oder Hotspot gefunden
        if delayPin==0 or hotspot_found:
            logger.info("Shutdown wird verzoegert um {:} min".format(MIN_DELAY_SHUTDOWN))
            time.sleep(MIN_DELAY_SHUTDOWN*60)

        # und tschüss
        u_bat=rlib.batteriespannung_messen(mcp)
        shutdown()
    except:
        logger.exception("Exception in main")
    
# Main program loop.
if __name__ == '__main__':
    main()
