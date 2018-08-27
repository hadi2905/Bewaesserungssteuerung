"""
Liest die Datei bewaesserung.json ein und schreibt alle Daten der letzten <N> Tage auf den Bildschirm
Es wird vorausgesetzt dass die JSON-Datei sich im lokalen Verzeichnis befindet

Parameter:
    nDays:  Anzahl Tage die angezeigt werden sollen. Default: 7
"""
import json
import datetime as dt
import sys


if len(sys.argv)>1 and sys.argv[1].isnumeric():
    nDays = int(sys.argv[1])
else:
    nDays = 7
    
fJson = open("bewaesserung.json", "r")
data = json.load(fJson)
fJson.close()

print("Datum;Batterie;Temperatur;rel.Luftfeuchtigkeit;abs.Luftfeuchtigkeit;Boden1;Boden2")
for i in data:
    if i[0][:10] >= str(dt.date.today()-dt.timedelta(days=nDays)):
        print("{:}\t{:}\t{:}\t{:}\t{:}\t{:}\t{:}".format(i[0][:16],i[1],i[2][0],i[2][1],i[2][2],i[3][0],i[3][1]).replace('.',','))
