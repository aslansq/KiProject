import os
from kiconst import KiConst
import jinja2
# this files is going to be used to auto layout in symbol editor

class KiSymEditPin:
        def __init__(self):
                self.pin = None # class KiPin type
                # positions
                self.x = 0
                self.y = 0
                self.deg = 0

        def parse(self, pin):
                self.pin = pin

class KiSymEditSym:
        def __init__(self):
                self.sym = None # class KiSymbol type
                self.pins = [] # class KiSymEditPin type
                # including ic name and box and pins
                self.width = 0
                self.height = 0

        def parse(self, sym):
                self.sym = sym

                for i in range(sym.numOfPins):
                        kiSymEditPin = KiSymEditPin()
                        kiSymEditPin.parse(sym.pins[i])
                        self.pins.append(kiSymEditPin)

class KiSymEditLib:
        def __init__(self):
                self.lib = None
                # this one does not have any physical items to be placed
                self.symbols = [] # class KiSymEditSym type
                self.outFileName = "" # just for debugging purposes
        
        def parse(self, lib):
                self.lib = lib
                for i in range(lib.numOfSymbols):
                        kiSymEditSym = KiSymEditSym()
                        kiSymEditSym.parse(lib.symbols[i])
                        self.symbols.append(kiSymEditSym)

        def gen(self, templateFilePath, outFolderPath):
                templateFileName = os.path.basename(templateFilePath)
                templateLoader = jinja2.FileSystemLoader(searchpath=os.path.dirname(templateFilePath))
                templateEnv = jinja2.Environment(loader=templateLoader)
                template = templateEnv.get_template(templateFileName)

                # change the filename to library name
                self.outFileName = templateFileName.replace(KiConst.invertedUniqDict["lib.name"], self.lib.name)

                outFilePath = os.path.join(outFolderPath, self.outFileName)
                renderedText = template.render(symbols = self.symbols,
                                               lib = self.lib)
                with open(os.path.join(outFolderPath, outFilePath), 'w') as f:
                        f.write(renderedText)
                print("Gen: " + str(outFilePath))