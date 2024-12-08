# this file is used for parsing information from csv
# pin without symbol does not make sense own it is own
# so pin should be instantiated inside of symbol class.
# symbol->lib and others follow same rule.
# nested class has not been used since, it creates indentation nightmare

from kiconst import KiConst
from kiutil import KiUtil
import csv
import os

# maybe this should not be here but it is easy to gather data here
class _KiGlobalConn:
        def __init__(self):
                self.nodes = []
                self.numOfNodes = 0
                self.dir = ""
                self.name = ""
        
        def parseFromCsv(self, pin):
                self.name = pin[KiConst.csv["sym"]] + "_" + pin[KiConst.csv["pin"]]
                self.nodes = pin[KiConst.csv["nodes"]].split('-')
                # remove itself
                self.dir = pin[KiConst.csv["pinDir"]]
                if self.dir == "input" and self.name in self.nodes:
                        self.nodes.remove(self.name)
                self.numOfNodes = len(self.nodes)

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
                # input, output
                self.dir = ""
                # inverted_clock, inverted, line, clock
                self.style = ""
                self.conn = _KiGlobalConn()
        
        def parseFromCsv(self, pin):
                self.name = pin[KiConst.csv["pin"]]
                self.dir = pin[KiConst.csv["pinDir"]]
                self.style = pin[KiConst.csv["pinStyle"]]
                if pin[KiConst.csv["nodes"]] != "":
                        self.conn.parseFromCsv(pin)

        def log(self, depth, pos):
                s = KiUtil.getLogDepthStr(depth, pos) + "PinName: " + self.name + " Dir: " + self.dir + " Style: " + self.style + " " + "\n"
                s = s + self.conn.log(depth + 1, 1) + "\n"
                return s

# Data structure model of a symbol
class _KiSymbol:
        def __init__(self):
                self.name = ""
                self.designator = ""
                self.numOfPins = 0
                self.pins = [] # class _KiLib.Pin type

        def parseFromCsv(self, symbol):
                # if empty just return
                if len(symbol) == 0:
                        return
                # at this point every item in should have same symbol name
                self.name = symbol[0][KiConst.csv["sym"]]
                self.designator = symbol[0][KiConst.csv["desig"]]
                # number of pins is just number of items
                self.numOfPins = len(symbol)

                for i in range(self.numOfPins):
                        # create a pin and parseFromCsv it
                        kiPin = _KiPin()
                        kiPin.parseFromCsv(symbol[i])
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

        def parseFromCsv(self, lib):
                # if empty library just return
                if len(lib) == 0:
                        return

                if len(lib[0]) < KiConst.csv["count"]:
                        print("invalid number of columns(" + str(len(lib[0])) +") in csv")
                        print(lib)
                        exit(1)
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

                for i in range(self.numOfSymbols):
                        # parsing symbols with entry and exist boundary
                        self.symbols[i].parseFromCsv(lib[lastLibIdx[i] : lastLibIdx[i+1]])

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

        def __isLibsConsecutive(self, rowList):
                libNames = []
                lastLibName = ""
                for i in range(len(rowList)):
                        libName = rowList[i][KiConst.csv["lib"]]
                        if libName != lastLibName:
                                lastLibName = libName
                                if libName in libNames:
                                        return False
                                libNames.append(libName)
                return True

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
                                                print("ERR: symbol name is not uniq->" + symNames[i])
                return isUniq

        def __isSymsConsecutive(self, rowList):
                if self.__isSymNamesUniq(rowList) == False:
                        return False

                symNames = []
                lastSymName = ""
                for i in range(len(rowList)):
                        symName = rowList[i][KiConst.csv["sym"]]
                        if symName != lastSymName:
                                lastSymName = symName
                                if symName in symNames:
                                        return False
                                symNames.append(symName)
                return True

        def __validate(self, rowList):
                for i in range(len(rowList)):
                        #at least it should have until nodes
                        if len(rowList[i]) < KiConst.csv["nodes"]:
                                return False
                        # if it has empty elements, not valid
                        # nodes can be empty
                        for j in range(KiConst.csv["nodes"]):
                                if rowList[i][j] == "":
                                        print("ERR: row in csv file has empty elements")
                                        print(rowList[i])
                                        return False

                if self.__isLibsConsecutive(rowList) == False:
                        return False

                if self.__isSymsConsecutive(rowList) == False:
                        return False

                return True

        def parseFromCsv(self, csvFilePath):
                self.name = str(os.path.basename(csvFilePath)).replace(".csv", "")
                with open(csvFilePath, newline='') as csvFile:
                        csvReader = csv.reader(csvFile)
                        rowList = []
                        for row in csvReader:
                                # if it is just new line just skip
                                if len(row) == 0:
                                        continue
                                if row[0][0] == "#":
                                        continue
                                # we dont care about white space or new line
                                for i in range(len(row)):
                                        row[i] = row[i].replace(" ", "")
                                        row[i] = row[i].strip()
                                rowList.append(row)
                        # if empty just return
                        if len(rowList) == 0:
                                return

                        if self.__validate(rowList) == False:
                                print("ERR: Csv file is not valid: " + str(csvFilePath))
                                exit(1)

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

                        for i in range(self.numOfLibs):
                                # parsing library with entry and exit boundary
                                self.libs[i].parseFromCsv(rowList[lastRowIdx[i] : lastRowIdx[i+1]])


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

