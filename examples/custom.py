from random import randint
import sys
import os
sys.path.append(os.path.join("..", "sources"))
from kiconst import KiConst

countries = {
    "USA": {
        "New York": ["New York", "Buffalo", "Rochester", "Albany"],
        "California": ["Los Angeles", "San Diego", "San Francisco", "San Jose"],
        "Texas": ["Houston", "Dallas", "Austin", "San Antonio"],
        "Florida": ["Miami", "Orlando", "Tampa"],
        "Illinois": ["Chicago", "Aurora", "Naperville", "Rockford"]
    },
    "Canada": {
        "Ontario": ["Toronto", "Ottawa", "Mississauga", "Brampton"],
        "British Columbia": ["Vancouver", "Victoria", "Surrey", "Burnaby"],
        "Quebec": ["Montreal", "Quebec City", "Laval", "Gatineau"],
        "Alberta": ["Calgary", "Edmonton", "Red Deer"],
        "Nova Scotia": ["Halifax", "Sydney"]
    },
    "Australia": {
        "New South Wales": ["Sydney", "Newcastle", "Wollongong"],
        "Victoria": ["Melbourne", "Geelong", "Ballarat"],
        "Queensland": ["Brisbane", "Gold Coast", "Cairns"],
        "Western Australia": ["Perth", "Mandurah", "Bunbury"],
        "South Australia": ["Adelaide", "Murray Bridge"]
    },
    "India": {
        "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik"],
        "Karnataka": ["Bangalore", "Mysore", "Mangalore"],
        "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai"],
        "Uttar Pradesh": ["Lucknow", "Kanpur", "Agra"],
        "West Bengal": ["Kolkata", "Durgapur", "Siliguri"]
    },
    "Germany": {
        "Bavaria": ["Munich", "Nuremberg", "Augsburg"],
        "North Rhine-Westphalia": ["Cologne", "Dusseldorf", "Dortmund"],
        "Baden-Wurttemberg": ["Stuttgart", "Mannheim", "Karlsruhe"],
        "Hesse": ["Frankfurt", "Wiesbaden", "Darmstadt"],
        "Berlin": ["Berlin"]
    },
    "France": {
        "Ile-de-France": ["Paris", "Versailles", "Saint-Denis"],
        "Azur": ["Marseille", "Nice", "Toulon"],
        "Auvergne-Rhone-Alpes": ["Lyon", "Grenoble", "Saint-Etienne"],
        "Nouvelle-Aquitaine": ["Bordeaux", "Limoges"]
    },
    "Brazil": {
        "Sao Paulo": ["Sao Paulo", "Campinas", "Santos"],
        "Rio de Janeiro": ["Rio de Janeiro", "Niteroi", "Cabo Frio"],
        "Minas Gerais": ["Belo Horizonte", "Uberlandia"],
        "Bahia": ["Salvador", "Feira de Santana"]
    },
    "Russia": {
        "Moscow": ["Moscow"],
        "Saint Petersburg": ["Saint Petersburg"],
        "Sverdlovsk": ["Yekaterinburg", "Nizhny Tagil"],
        "Krasnoyarsk": ["Krasnoyarsk", "Norilsk"]
    },
    "Japan": {
        "Tokyo": ["Tokyo", "Yokohama", "Chiba"],
        "Osaka": ["Osaka", "Kobe"],
        "Hokkaido": ["Sapporo", "Hakodate"],
        "Okinawa": ["Naha", "Okinawa City"]
    }
}

r = ["#Library", "Symbol", "SymbolDesignator", "PinName", "PinNumber", "PinDir", "PinStyle", "Connector"]
rows = []
rows.append(r)
for keyCountry in countries:
        for keyCity in countries[keyCountry]:
                ordinalNumber = 1
                for province in countries[keyCountry][keyCity]:
                        r = []
                        r.append(keyCountry) # library
                        r.append(keyCity) # Symbol
                        r.append(keyCity) # SymbolDesignator
                        r.append(province) # PinName
                        r.append(str(ordinalNumber)) # PinNumber
                        dir = ["output", "input"]
                        dir = dir[randint(0,1)]
                        r.append(dir) #PinDir
                        style = ["inverted_clock", "inverted", "line", "clock"]
                        style = style[randint(0,3)]
                        r.append(style) #PinStyle
                        if dir == "output":
                                r.append(keyCity + "_" + province) # Connector
                        else:
                                r.append("") # Connector
                        for i in range(len(r)):
                                r[i] = r[i].replace(" ", "")
                                r[i] = r[i].replace("-", "")
                        rows.append(r)
                        ordinalNumber = ordinalNumber + 1

outputRowIdxs = []
for r in range(len(rows)):
        if rows[r][KiConst.csv["pinDir"]] == "output":
                outputRowIdxs.append(r)

for i in range(1, len(rows)):
        if rows[i][KiConst.csv["pinDir"]] == "output":
                continue

        numOfConnection = randint(0,1)
        if numOfConnection == 0:
                continue
        
        choosenOutRowIdxs = []
        for j in range(numOfConnection):
                outRowIdx = outputRowIdxs[randint(0,len(outputRowIdxs)-1)]
                if not outRowIdx in choosenOutRowIdxs:
                        choosenOutRowIdxs.append(outRowIdx)
                        
        newName = rows[i][KiConst.csv["sym"]] + "_" + rows[i][KiConst.csv["pin"]]
        for choosenOutRowIdx in choosenOutRowIdxs:
                choosenOutRowConnName = rows[choosenOutRowIdx][KiConst.csv["nodes"]]
                newName = newName + "-" + choosenOutRowConnName
                
        rows[i][KiConst.csv["nodes"]] = newName

for outRowIdx in outputRowIdxs:
        outNodeName = rows[outRowIdx][KiConst.csv["nodes"]]
        isUsed = False
        for j in range(len(rows)):
                if j == outRowIdx:
                        continue
                if rows[j][KiConst.csv["pinDir"]] == "output":
                        continue
                if outNodeName in rows[j][KiConst.csv["nodes"]]:
                        isUsed = True
                        break
        if not isUsed:
                rows[outRowIdx][KiConst.csv["nodes"]] = ""

for row in rows:
        s = ""
        for col in row:
                if s == "":
                        s = col
                else:
                        s = s + "," + col
        s = s + ","
        print(s)