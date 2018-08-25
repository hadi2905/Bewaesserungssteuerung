# -*- coding: utf-8 -*-
import json
import logging
from pathlib import Path


"""
    Logik Modul für Bewässerungssteuerung
    

"""


def read_json_cfg():
    """
    In JSON codierte Konfigurationsdatei einlesen
    """
    # Falls Datei bewaesserung.cfg noch nicht existiert, beginnen wir mit Defaultwerten
    try:
        home = str(Path.home())
        fJson = open(home + "/data/bewaesserung.cfg", "r")
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
        home = str(Path.home())
        fJson = open(home + "/data/" + cfgData['Messwerte_Datei'], "r")
        data = json.load(fJson)
        fJson.close()
    except FileNotFoundError:
        data = []    

    return data


def save_json(cfgData, data):
        home = str(Path.home())

        fJson = open(home + "/data/" + cfgData['Messwerte_Datei'], "w")
        json.dump(data, fJson)
        fJson.close()

        fJson = open(home + "/data/bewaesserung.cfg", "w")
        json.dump(cfgData, fJson)
        fJson.close()
        
    
