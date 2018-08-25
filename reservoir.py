#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
import datetime as dt
import logging
import RPi.GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008 as MCP3008


class Reservoir:
    """
    Klasse zum Messen und Überwachen des Wasserstands in einem Gefäß
    """

    def __init__(self, pinMess, kanal1, kanal2, kanal3, pinPump):
        """
        Initialisiert das Reservoir
        pinMess: Raspi_pin der Messspannung liefert, kanal1-kanal3: Kanäle des Analog-Digital-Konvertes für die Messfühler, pinPump: Raspi-Pin zum Schalten der Pumpe
        """
        self.logger = logging.getLogger()
        self.SCHWELLE = 500
        self.v_pin = pinMess
        self.ch1 = kanal1
        self.ch2 = kanal2
        self.ch3 = kanal3
        self.p_pin = pinPump
        self.mcp = MCP3008.MCP3008(spi=SPI.SpiDev(0, 0))
        GPIO.setup(self.v_pin, GPIO.OUT)
        GPIO.setup(self.p_pin, GPIO.OUT)
        self.pumpe("off")
        # Ausgabe in Datei vorbereiten
        #fH = open("/home/pi/hydro_output.txt", "a", 0) 

    def pumpe(self, val):
        """
        Schaltet die Pumpe in Abhängigkeit von val "on"/"off"
        """
        GPIO.output(self.p_pin, 1 if val=="on" else 0)
        
    def holeSensordaten(self):
        """
        Liest die digitalisierten Werte der drei Wasserstandsmessfühler ein
        """
        GPIO.output(self.v_pin,1)   # Messspannung einschalten
        time.sleep(0.4)
        self.m1 = self.mcp.read_adc(self.ch1)
        self.m2 = self.mcp.read_adc(self.ch2)
        self.m3 = self.mcp.read_adc(self.ch3)
        self.logger.debug("Messfuehler {:>4}{:>4}{:>4}".format(self.m1, self.m2, self.m3))
        GPIO.output(self.v_pin,0)
        
    def gibStand(self):
        """
        Gib den Wasserstand als Integer 0-3 zurück
        """
        self.holeSensordaten()
        if self.m3 < self.SCHWELLE:
            ret = 3
        elif self.m2 < self.SCHWELLE:
            ret = 2
        elif self.m1 < self.SCHWELLE:
            ret = 1
        else: 
            ret = 0
        self.logger.debug("Reservoir.gibStand={:}".format(ret))
        return ret
        
    def fuelleBisLevel(self, lev):
        """
        Startet die Pumpe und füllt das Reservoir bis zum angegebenen Level (1-3)
        Falls nach jeweils 10 Sek nicht mindestens ein nächster Level erreicht ist, gehen wir davon aus dass der Speicher leer ist oder eine sonstige
        Störung die Pumpe an ihrer Funktion hindert. Dann wird die Pumpe abgeschaltet und die Funktion gibt den bis dahin erreichten Level zurück
        """
        self.logger.info("Reservoir.fuelleBisLevel:{:}".format(lev))
        lev_akt = self.gibStand()
        start = dt.datetime.now()
        
        if lev_akt < lev:
            self.logger.debug("Schalte Pumpe ein")
            self.pumpe("on")
            # Schleife bis gewünschter Level erreicht oder Zeitlimit (10 sek/Level) überschritten ist
            while lev_akt < lev:
                time.sleep(1)
                lev_akt = self.gibStand()
                self.logger.debug("Aktueller Stand: {:}".format(lev_akt))
                jetzt = dt.datetime.now()
                if (jetzt-start).seconds > (lev_akt+1)*40:  # 40 Sekunden je Stufe
                    self.logger.warning("Abbruch nach {:} Sekunden".format((jetzt-start).seconds))
                    break
                
            self.logger.debug("Schalte Pumpe aus")
            self.pumpe("off")

        return lev_akt

