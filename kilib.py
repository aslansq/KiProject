from kiconst import KiConst
from kiutil import KiUtil
class KiPin:
        def __init__(self):
                self.name = ""
                # input, output
                self.dir = ""
                # inverted_clock, inverted, line, clock
                self.style = ""
        
        def parse(self, pin):
                self.name = pin[KiConst.CSV_COL_PIN_NAME]
                self.dir = pin[KiConst.CSV_COL_PIN_DIR]
                self.style = pin[KiConst.CSV_COL_PIN_STYLE]
        
        def info(self, depth, pos):
                s = KiUtil.getInfoDepthStr(depth, pos) + self.name + " " + self.dir + " " + self.style + " " + "\n"
                return s

class KiSymbol:
        def __init__(self):
                self.name = ""
                self.designator = ""
                self.numOfPins = 0
                self.pins = [] # class KiLib.Pin type

        def parse(self, symbol):
                # if empty just return
                if len(symbol) == 0:
                        return
                # at this point every item in should have same symbol name
                self.name = symbol[0][KiConst.CSV_COL_SYM_NAME]
                self.designator = symbol[0][KiConst.CSV_COL_SYM_DESIG]
                # number of pins is just number of items
                self.numOfPins = len(symbol)

                for i in range(self.numOfPins):
                        # create a pin and parse it
                        kiPin = KiPin()
                        kiPin.parse(symbol[i])
                        self.pins.append(kiPin)
        
        def info(self, depth, pos):
                s = KiUtil.getInfoDepthStr(depth, pos) + self.name + " " + self.designator + " " + "\n"
                for i in range(self.numOfPins):
                        s = s + self.pins[i].info(depth + 1, i + 1)
                return s

class KiLib:
        def __init__(self):
                self.name = ""
                self.numOfSymbols = 0
                self.symbols = [] # class Symbol type

        def parse(self, lib):
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
                        self.symbols[i].parse(lib[lastLibIdx[i] : lastLibIdx[i+1]])

        def info(self, depth, pos):
                s = KiUtil.getInfoDepthStr(depth, pos) + self.name + " " + "\n"
                for i in range(self.numOfSymbols):
                        s = s + self.symbols[i].info(depth + 1, i + 1)
                return s
