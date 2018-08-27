# -*- coding: utf-8 -*-
"""
    Logik Modul für Bewässerungssteuerung
    Enthält Funktionalität die keine Raspi-spezifischen Elemente (GPIO, Adafruit, Realtime Clock) benötigt
"""
import json
import logging


def read_json_cfg():
    """
    In JSON codierte Konfigurationsdatei /home/pi/data/bewaesserung.cfg einlesen
    Falls Datei noch nicht existiert, beginnen wir mit Defaultwerten
    """
    try:
        fJson = open("/home/pi/data/bewaesserung.cfg", "r")
        data = json.load(fJson)
        fJson.close()
    except FileNotFoundError:
        data = {  'Anzahl_kein_Wasser' : 0
                , 'Messwerte_Datei' : 'bewaesserung.json'
                , 'Bewaesserungsstunden' : (7,19)
                , 'Bewaesserung_aktiv' : True
                }

    logging.getLogger().debug("Config-Datei eingelesen")
    return data


def read_json_data(cfgData):
    """
    In JSON codierte Messdatendatei einlesen
    """
    # Falls Datei bewaesserung.json noch nicht existiert, beginnen wir mit einer leeren Datenstruktur
    try:
        fJson = open("/home/pi/data/" + cfgData['Messwerte_Datei'], "r")
        data = json.load(fJson)
        fJson.close()
    except FileNotFoundError:
        data = []    

    return data


def save_json(cfgData, data):
    """
    In JSON codierte Konfigurations- und Messdatendatei schreiben
    """
    fJson = open("/home/pi/data/" + cfgData['Messwerte_Datei'], "w")
    json.dump(data, fJson)
    fJson.close()

    fJson = open("/home/pi/data/bewaesserung.cfg", "w")
    json.dump(cfgData, fJson)
    fJson.close()
        
    
