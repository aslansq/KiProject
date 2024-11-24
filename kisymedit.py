import os
from kiconst import KiConst
from kiutil import KiUtil
import jinja2
# this files is going to be used to auto layout in symbol editor

class KiSymEditPin:
        def __init__(self):
                self.pin = None # class KiPin type
                # positions
                self.x = 0
                self.y = 0
                self.deg = 0
                self.dirIdx = 0
                # storing copy in every pin is not needed but it makes things very easy
                self.dirMaxNameLenAll = 0

        def parse(self, pin):
                self.pin = pin
        
        def prepareForAutoLayout(self, dirIdx, dirMaxNameLenAll):
                self.dirIdx = dirIdx
                self.dirMaxNameLenAll = dirMaxNameLenAll

        def autoLayout(self):
                if self.dirIdx == 0:
                        self.y = -KiConst.symEdit["firstPinyOffset"]
                else:
                        self.y = -KiConst.symEdit["firstPinyOffset"]
                        self.y = self.y - (self.dirIdx * KiConst.symEdit["heightBetweenPins"])

                if self.pin.dir == "output":
                        self.deg = 180
                        self.x = (self.dirMaxNameLenAll["input"] + self.dirMaxNameLenAll["output"]) * KiConst.symEdit["charWidth"]
                        self.x = self.x + KiConst.symEdit["lenPin"] * 2 + KiConst.symEdit["spaceBetweenInNOutPin"]


        def info(self, depth, pos):
                s = KiUtil.getInfoDepthStr(depth, pos) + self.pin.name + " x " + str(self.x) + " y " + str(self.y) 
                s = s + " deg " + str(self.deg) + " dirIdx " + str(self.dirIdx) + " dir " + self.pin.dir + "\n"
                return s

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

        def prepareForAutoLayout(self):
                dirIdx = {
                        "input"  : 0,
                        "output" : 0
                }
                dirMaxNameLen = {
                        "input" : 0,
                        "output": 0
                }
                for i in range(self.sym.numOfPins):
                        nameLen = len(self.sym.pins[i].name)
                        if nameLen > dirMaxNameLen[self.sym.pins[i].dir]:
                                dirMaxNameLen[self.sym.pins[i].dir] = nameLen

                for i in range(self.sym.numOfPins):
                        self.pins[i].prepareForAutoLayout(dirIdx[self.sym.pins[i].dir],
                                                          dirMaxNameLen)
                        dirIdx[self.sym.pins[i].dir] = dirIdx[self.sym.pins[i].dir] + 1

        def autoLayout(self):
                for i in range(self.sym.numOfPins):
                        self.pins[i].autoLayout()

        def info(self, depth, pos):
                s = KiUtil.getInfoDepthStr(depth, pos) + self.sym.name +  " w " + str(self.width) + " h " + str(self.height) + "\n"
                for i in range(self.sym.numOfPins):
                        s = s + self.pins[i].info(depth + 1, i + 1)
                return s

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

        def prepareForAutoLayout(self):
                for i in range(self.lib.numOfSymbols):
                        self.symbols[i].prepareForAutoLayout()

        def autoLayout(self):
                for i in range(self.lib.numOfSymbols):
                        self.symbols[i].autoLayout()

        def info(self, depth, pos):
                s = KiUtil.getInfoDepthStr(depth, pos) + self.lib.name + "\n"
                for i in range(self.lib.numOfSymbols):
                        s = s + self.symbols[i].info(depth + 1, i + 1)
                return s

        def gen(self, templateFilePath, outFolderPath):
                self.prepareForAutoLayout()
                self.autoLayout()
                print(self.info(0, 1))
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