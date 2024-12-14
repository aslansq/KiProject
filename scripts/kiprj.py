# this file is used for parsing information from csv
# pin without symbol does not make sense own it is own
# so pin should be instantiated inside of symbol class.
# symbol->lib and others follow same rule.
# nested class has not been used since, it creates indentation nightmare

from kiconst import KiConst
from kiutil import KiUtil
import csv
import os
from io import StringIO

# maybe this should not be here but it is easy to gather data here
# Data structure of global connector. a connector can contain multiple nodes(aka global labels)
class _KiGlobalConn:
        def __init__(self):
                self.nodes = []
                self.numOfNodes = 0
                self.type = ""
                self.name = ""
                self.pos = ""
                self.idx = 0
                self.uuid = ""
        
        def parse(self, parentUuid, pin, idx):
                self.idx = idx
                self.name = pin[KiConst.csv["sym"]] + "_" + pin[KiConst.csv["pin"]]
                self.nodes = pin[KiConst.csv["nodes"]].split('-')
                self.type = pin[KiConst.csv["pinType"]]
                self.pos = pin[KiConst.csv["pinPos"]]
                self.numOfNodes = len(self.nodes)
                self.uuid = KiUtil.getUuid("_KiGlobalConn" +
                                           parentUuid +
                                           self.name +
                                           str(self.idx))

        def log(self, depth, pos):
                if self.numOfNodes == 0:
                        return ""
                s = KiUtil.getLogDepthStr(depth, pos) + "Nodes: "
                for i in range(self.numOfNodes):
                        s = s + self.nodes[i] + " "
                return s

# Data structure model of a pin
class _KiPin:
        def __init__(self):
                self.name = ""
                # KiConst.availPinStyles
                self.style = ""
                # KiConst.availPinTypes
                self.type = ""
                # so we choosed to have a connector for each pin but they can be empty
                self.conn = _KiGlobalConn()
                self.number = ""
                self.pos = ""
                self.idx = 0
                self.uuid = ""
        
        def parse(self, parentUuid, pin, idx):
                self.idx = idx
                self.name = pin[KiConst.csv["pin"]]
                self.type = pin[KiConst.csv["pinType"]]
                self.style = pin[KiConst.csv["pinStyle"]]
                self.number = pin[KiConst.csv["pinNumber"]]
                self.pos = pin[KiConst.csv["pinPos"]]
                self.uuid = KiUtil.getUuid("_KiPin" +
                                           parentUuid +
                                           self.name +
                                           str(self.idx))
                if pin[KiConst.csv["nodes"]] != "":
                        self.conn.parse(self.uuid, pin, self.idx)

        def log(self, depth, pos):
                s = KiUtil.getLogDepthStr(depth, pos) + "PinName: " + self.name + " Pos: " + self.pos + " Style: " + self.style + " " + "\n"
                s = s + self.conn.log(depth + 1, 1) + "\n"
                return s

# Data structure model of a symbol
class _KiSymbol:
        def __init__(self):
                self.name = ""
                self.designator = ""
                self.numOfPins = 0
                self.pins = [] # class _KiLib.Pin type
                self.idx = 0
                self.uuid = ""

        def parse(self, parentUuid, symbol, idx):
                # if empty just return
                if len(symbol) == 0:
                        return
                self.idx = idx
                # at this point every item in should have same symbol name
                self.name = symbol[0][KiConst.csv["sym"]]
                self.designator = symbol[0][KiConst.csv["desig"]]
                # number of pins is just number of items
                self.numOfPins = len(symbol)

                self.uuid = KiUtil.getUuid("_KiSymbol" +
                                           parentUuid +
                                           self.name +
                                           str(self.idx))

                for i in range(self.numOfPins):
                        # create a pin and parse it
                        kiPin = _KiPin()
                        kiPin.parse(self.uuid, symbol[i], i)
                        self.pins.append(kiPin)

        def log(self, depth, pos):
                s = KiUtil.getLogDepthStr(depth, pos) + "SymName: " + self.name + " DesigName" + self.designator + " " + "\n"
                for i in range(self.numOfPins):
                        s = s + self.pins[i].log(depth + 1, i + 1)
                return s

# Data structure model of a library
class _KiLib:
        def __init__(self):
                self.name = ""
                self.numOfSymbols = 0
                self.symbols = [] # class Symbol type
                self.idx = 0
                self.uuid = ""

        def parse(self, parentUuid, lib, idx):
                # if empty library just return
                if len(lib) == 0:
                        return
                self.idx = idx
                self.name = lib[0][KiConst.csv["lib"]]

                lastSymbolName = ""
                lastLibIdx = []
                # deducing entry and exit boundary of symbol in the library
                for i in range(len(lib)):
                        # creating new library for every different symbol name found in the library
                        if lib[i][KiConst.csv["sym"]] != lastSymbolName:
                                kiSymbol = _KiSymbol()
                                self.symbols.append(kiSymbol)
                                # storing idx that I found different symbol name
                                lastLibIdx.append(i)
                                lastSymbolName = lib[i][KiConst.csv["sym"]]
                self.numOfSymbols = len(self.symbols)
                # for loop wont detect last item symbol name change so added myself
                lastLibIdx.append(len(lib))

                self.uuid = KiUtil.getUuid("_KiLib" +
                                           parentUuid +
                                           self.name +
                                           str(self.idx))
                for i in range(self.numOfSymbols):
                        # parsing symbols with entry and exist boundary
                        self.symbols[i].parse(self.uuid, lib[lastLibIdx[i] : lastLibIdx[i+1]], i)

        def log(self, depth, pos):
                s = KiUtil.getLogDepthStr(depth, pos) + "LibName: " + self.name + " " + "\n"
                for i in range(self.numOfSymbols):
                        s = s + self.symbols[i].log(depth + 1, i + 1)
                return s

class KiPrj:
        def __init__(self, logFolderPath):
                self.name = ""
                self.numOfLibs = 0
                self.libs = [] # class _KiLib type
                self.logFolderPath = logFolderPath
                self.uuid = ""

        def __isLibsConsecutive(self, rowList):
                libNames = []
                lastLibName = ""
                for i in range(len(rowList)):
                        libName = rowList[i][KiConst.csv["lib"]]
                        if libName != lastLibName:
                                lastLibName = libName
                                if libName in libNames:
                                        raise Exception("Lib(" + libName + ") is not consecutive")
                                libNames.append(libName)

        def __isSymNamesUniq(self, rowList):
                # purposes of this function not to have same symbol name in different libraries
                libSymNames = []
                for i in range(len(rowList)):
                        # ?? because I dont think anyone will put questions marks in their symbol or library names
                        libSymName = rowList[i][KiConst.csv["lib"]] + "??" + rowList[i][KiConst.csv["sym"]]
                        if not libSymName in libSymNames:
                                libSymNames.append(libSymName)

                symNames = []
                for i in range(len(libSymNames)):
                        symNames.append(libSymNames[i].split("??")[1])

                isUniq = len(symNames) == len(set(symNames))
                if isUniq == False:
                        for i in range(len(symNames)):
                                for j in range(i, len(symNames)):
                                        if symNames[i] == symNames[j]:
                                                raise Exception("ERR: symbol name is not uniq->" + symNames[i])

        def __isSymsConsecutive(self, rowList):
                self.__isSymNamesUniq(rowList)

                symNames = []
                lastSymName = ""
                for i in range(len(rowList)):
                        symName = rowList[i][KiConst.csv["sym"]]
                        if symName != lastSymName:
                                lastSymName = symName
                                if symName in symNames:
                                        raise Exception("ERR symbol name is not consecutive->" + symName)
                                symNames.append(symName)

        def __isPinNumbersNumeric(self, rowList):
                for i in range(len(rowList)):
                        if rowList[i][KiConst.csv["pinNumber"]].isnumeric() == False:
                                raise Exception("ERR pin number is not numeric. "  + str(rowList[i]))

        def __isPinNumbersUniqInSymbol(self, rowList):
                dict = {}
                for i in range(len(rowList)):
                        name = rowList[i][KiConst.csv["sym"]]
                        pinNumber = rowList[i][KiConst.csv["pinNumber"]]
                        if not name in dict:
                                dict.update({name : [pinNumber]})
                        else:
                                dict[name].append(pinNumber)
                
                for key in dict.keys():
                        if len(dict[key]) != len(set(dict[key])):
                                raise Exception("ERR Pin numbers are not unique in " + str(key))

        def __isPinTypeSupported(self, rowList):
                for i in range(len(rowList)):
                        type = rowList[i][KiConst.csv["pinType"]]
                        if type in KiConst.availPinTypes:
                                #supported
                                continue
                        s = "ERR unsupported pin type(" + type + ")\n"
                        s = s + str(rowList[i])
                        raise Exception(s)
        
        def __isPinStyleSupported(self, rowList):
                for i in range(len(rowList)):
                        style = rowList[i][KiConst.csv["pinStyle"]]
                        if not style in KiConst.availPinStyles:
                                s = "ERR unsupported pin style(" + style + ")\n"
                                s = s + str(rowList[i])
                                raise Exception(s)

        def __validate(self, rowList):
                for i in range(len(rowList)):
                        #at least it should have until nodes
                        if len(rowList[i]) < KiConst.csv["nodes"]:
                                return False
                        # if it has empty elements, not valid
                        # nodes can be empty
                        for j in range(KiConst.csv["pinStyle"]):
                                if rowList[i][j] == "":
                                        s = "ERR: row in csv file has empty elements. columnIdx = " + str(j) + "\n"
                                        s = s + str(rowList[i])
                                        raise Exception(s)

                self.__isPinNumbersNumeric(rowList)

                self.__isLibsConsecutive(rowList)

                self.__isSymsConsecutive(rowList)
                
                self.__isPinNumbersUniqInSymbol(rowList)

                self.__isPinTypeSupported(rowList)

                self.__isPinStyleSupported(rowList)

        def __getRowList(self, s):
                f = StringIO(s)
                csvReader = csv.reader(f)
                rowList = []
                for row in csvReader:
                        # if it is just new line just skip
                        if len(row) == 0:
                                continue
                        if row[0][0] == "#":
                                continue
                        # we dont care about white space or new line
                        for i in range(len(row)):
                                row[i] = str(row[i])
                                row[i] = row[i].replace(" ", "")
                                row[i] = row[i].strip()
                        rowList.append(row)
                return rowList

        def parseFromStr(self, name, s):
                self.name = name
                rowList = self.__getRowList(s)
                # if empty just return
                if len(rowList) == 0:
                        return

                self.__validate(rowList)

                lastLibName = ""
                lastRowIdx = []
                # deducing entry and exit boundary of a library in csv file
                for i in range(len(rowList)):
                        # creating new library for every different library name found in csv file
                        if rowList[i][KiConst.csv["lib"]] != lastLibName:
                                kiLib = _KiLib()
                                self.libs.append(kiLib)
                                # storing idx that I found different library name
                                lastRowIdx.append(i)
                                lastLibName = rowList[i][KiConst.csv["lib"]]
                self.numOfLibs = len(self.libs)
                # for loop wont detect last item library name change so added myself
                lastRowIdx.append(len(rowList))

                self.uuid = KiUtil.getUuid("KiPrj" + self.name)
                for i in range(self.numOfLibs):
                        # parsing library with entry and exit boundary
                        self.libs[i].parse(self.uuid, rowList[lastRowIdx[i] : lastRowIdx[i+1]], i)

        def parse(self, csvFilePath):
                name = str(os.path.basename(csvFilePath)).replace(".csv", "")
                with open(csvFilePath, newline='') as csvFile:
                        s = csvFile.read()
                        try:
                                self.parseFromStr(name, s)
                        except Exception as e:
                                s = str(csvFilePath) + " is not valid.\n"
                                s = s + str(e) + "\n"
                                raise Exception(s)

        def log(self):
                depth = 0
                pos = 1
                s = KiUtil.getLogDepthStr(depth, pos) + "PrjName: "+ self.name + " NumOfLibs" + str(self.numOfLibs) + "\n"
                for i in range(self.numOfLibs):
                        s = s + self.libs[i].log(depth + 1, i + 1)
                absOutFolderPath = os.path.join(self.logFolderPath, self.name)
                if not os.path.exists(absOutFolderPath):
                        os.makedirs(absOutFolderPath)
                absOutFilePath = os.path.join(absOutFolderPath, "KiPrj.txt")
                with open(absOutFilePath, 'w') as f:
                        f.write(s)

