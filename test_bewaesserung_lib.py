import bewaesserung_lib as lib
import logging
import reservoir_dummy as res

# Logger initialisieren
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
fH = logging.FileHandler("./test_bewaesserung_lib.log")
fH.setLevel(logging.DEBUG)
cH = logging.StreamHandler()
cH.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fH.setFormatter(formatter)
cH.setFormatter(formatter)
logger.addHandler(fH)
logger.addHandler(cH)

# Messwerte und Konfigurationsdaten aus Dateien lesen
cfgData = lib.read_json_cfg()
data = lib.read_json_data(cfgData)

#print(data)
#print(cfgData)
zielLevel = 3

if cfgData['Bewaesserung_aktiv']:
    if 7 in cfgData['Bewaesserungsstunden']:
        if cfgData['Anzahl_kein_Wasser'] <= 2:
            logger.info("Bewässerung kann starten")
            r = res.Reservoir(18,0,1,2,15)
            print(r.gibStand())
            ret = r.fuelleBisLevel(zielLevel)
            if ret==zielLevel:
                logger.info("Reservoir konnte auf Ziellevel {:} gefüllt werden".format(zielLevel))
                cfgData['Anzahl_kein_Wasser'] = 0
            else:
                logger.info("Füllung Reservoir nur bis Level {:} statt {:} möglich".format(ret, zielLevel))
                cfgData['Anzahl_kein_Wasser'] = cfgData['Anzahl_kein_Wasser'] + 1
        else:
            logger.info("Abbruch da bei den letzten beiden Versuchen kein Wasser verfügbar war")
    else:
        logger.info("keine Uhrzeit für Bewässerung")
else:
    logger.info("Bewässerung ist nicht aktiviert")
    
lib.save_json(cfgData, data)
