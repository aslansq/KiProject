from kiconst import KiConst
from kiutil import KiUtil

# maybe this should not be here but it is easy to gather data here
class KiGlobalConn:
        def __init__(self):
                self.nodes = []
                self.numOfNodes = 0
        
        def parseFromCsv(self, conn):
                self.nodes = conn.split('-')
                self.numOfNodes = len(self.nodes)

        def info(self, depth, pos):
                s = KiUtil.getInfoDepthStr(depth, pos)
                for i in range(self.numOfNodes):
                        s = s + self.nodes[i] + " "
                return s

# Data structure model of a pin
class KiPin:
        def __init__(self):
                self.name = ""
                # input, output
                self.dir = ""
                # inverted_clock, inverted, line, clock
                self.style = ""
                self.conn = None
                self.connExist = False
        
        def parseFromCsv(self, pin):
                self.name = pin[KiConst.CSV_COL_PIN_NAME]
                self.dir = pin[KiConst.CSV_COL_PIN_DIR]
                self.style = pin[KiConst.CSV_COL_PIN_STYLE]
                if pin[KiConst.CSV_COL_PIN_NODES] != "":
                        self.conn = KiGlobalConn()
                        self.conn.parseFromCsv(pin[KiConst.CSV_COL_PIN_NODES])
                        self.connExist = True

        def info(self, depth, pos):
                s = KiUtil.getInfoDepthStr(depth, pos) + self.name + " " + self.dir + " " + self.style + " " + "\n"
                if self.connExist:
                        # if it even exist there is only one always
                        s = s + self.conn.info(depth + 1, 1) + "\n"
                return s

# Data structure model of a symbol
class KiSymbol:
        def __init__(self):
                self.name = ""
                self.designator = ""
                self.numOfPins = 0
                self.pins = [] # class KiLib.Pin type

        def parseFromCsv(self, symbol):
                # if empty just return
                if len(symbol) == 0:
                        return
                # at this point every item in should have same symbol name
                self.name = symbol[0][KiConst.CSV_COL_SYM_NAME]
                self.designator = symbol[0][KiConst.CSV_COL_SYM_DESIG]
                # number of pins is just number of items
                self.numOfPins = len(symbol)

                for i in range(self.numOfPins):
                        # create a pin and parseFromCsv it
                        kiPin = KiPin()
                        kiPin.parseFromCsv(symbol[i])
                        self.pins.append(kiPin)
        
        def info(self, depth, pos):
                s = KiUtil.getInfoDepthStr(depth, pos) + self.name + " " + self.designator + " " + "\n"
                for i in range(self.numOfPins):
                        s = s + self.pins[i].info(depth + 1, i + 1)
                return s

# Data structure model of a library
class KiLib:
        def __init__(self):
                self.name = ""
                self.numOfSymbols = 0
                self.symbols = [] # class Symbol type

        def parseFromCsv(self, lib):
                # if empty library just return
                if len(lib) == 0:
                        return

                if len(lib[0]) < KiConst.CSV_COL_COUNT:
                        print("invalid number of columns(" + str(len(lib[0])) +") in csv")
                        print(lib)
                        exit(1)
                self.name = lib[0][KiConst.CSV_COL_LIB_NAME]

                lastSymbolName = ""
                lastLibIdx = []
                # deducing entry and exit boundary of symbol in the library
                for i in range(len(lib)):
                        # creating new library for every different symbol name found in the library
                        if lib[i][KiConst.CSV_COL_SYM_NAME] != lastSymbolName:
                                kiSymbol = KiSymbol()
                                self.symbols.append(kiSymbol)
                                # storing idx that I found different symbol name
                                lastLibIdx.append(i)
                                lastSymbolName = lib[i][KiConst.CSV_COL_SYM_NAME]
                self.numOfSymbols = len(self.symbols)
                # for loop wont detect last item symbol name change so added myself
                lastLibIdx.append(len(lib))

                for i in range(self.numOfSymbols):
                        # parsing symbols with entry and exist boundary
                        self.symbols[i].parseFromCsv(lib[lastLibIdx[i] : lastLibIdx[i+1]])

        def info(self, depth, pos):
                s = KiUtil.getInfoDepthStr(depth, pos) + self.name + " " + "\n"
                for i in range(self.numOfSymbols):
                        s = s + self.symbols[i].info(depth + 1, i + 1)
                return s
