import json


fJson = open("bewaesserung.json", "r")
data = json.load(fJson)
fJson.close()

print("Datum;Batterie;Temperatur;rel.Luftfeuchtigkeit;abs.Luftfeuchtigkeit;Boden1;Boden2")
for i in data:
    if i[0][:10] >= '2018-06-23':
        print("{:}\t{:}\t{:}\t{:}\t{:}\t{:}\t{:}".format(i[0][:16],i[1],i[2][0],i[2][1],i[2][2],i[3][0],i[3][1]).replace('.',','))
