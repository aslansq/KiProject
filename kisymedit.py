# this file is going to be used for auto layout in symbol editor
# this is a wrapper for KiPrj with layout locations for symbol editor
import os
from kiconst import KiConst
from kiutil import KiUtil
import jinja2

class _KiSymEditPin:
        def __init__(self):
                self.pin = None # class KiPin type
                # positions
                self.x = 0
                self.y = 0
                self.deg = 0
                self.dirIdx = 0
                # storing copy in every pin is not needed but it makes things very easy
                self.dirMaxNameLenAll = {
                        "input" : 0,
                        "output": 0
                }
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

                # see KiConst.symEdit comment to understand this
                if self.pin.dir == "output":
                        self.deg = 180
                        isInPinExist = False
                        if self.dirMaxNameLenAll["input"] != 0:
                                isInPinExist = True
                        if isInPinExist:
                                self.x = self.x + KiConst.symEdit["lenPin"] + \
                                         KiConst.symEdit["pinEndToPinName"] + \
                                         (self.dirMaxNameLenAll["input"] * KiConst.symEdit["charWidth"]) + \
                                         KiConst.symEdit["spaceBetweenInNOutPin"]
                        else:
                                self.x = self.x + KiConst.symEdit["spaceBetweenBoxNPinName"]
                        self.x = self.x + \
                                (self.dirMaxNameLenAll["output"] * KiConst.symEdit["charWidth"]) + \
                                KiConst.symEdit["pinEndToPinName"] + \
                                (KiConst.symEdit["lenPin"]-KiConst.symEdit["pinToBoxWidth"])

        def log(self, depth, pos):
                s = KiUtil.getLogDepthStr(depth, pos) + "PinName: " + self.pin.name + " x " + str(self.x) + " y " + str(self.y) 
                s = s + " deg " + str(self.deg) + " dirIdx " + str(self.dirIdx) + " dir " + self.pin.dir + "\n"
                return s

class _KiSymEditSym:
        def __init__(self):
                self.sym = None # class KiSymbol type
                self.symEditPins = [] # class _KiSymEditPin type
                # box edge positions
                self.x0 = 0
                self.x1 = 0
                self.y0 = 0
                self.y1 = 0
                # including ic name and box and pins
                self.width = 0
                self.height = 0
                # just the box
                self.boxWidth = 0
                self.boxHeight = 0
                self.isInPinExist = False
                self.isOutPinExist = False

        def parse(self, sym):
                self.sym = sym
                for i in range(sym.numOfPins):
                        kiSymEditPin = _KiSymEditPin()
                        kiSymEditPin.parse(sym.pins[i])
                        self.symEditPins.append(kiSymEditPin)

        def __calcBoxWidthHeight(self, dirIdx, dirMaxNameLen):
                #   |-------------------------------------------------------------|
                #   |lenPin-pinToBoxWidth                                         |
                #   |↓ ↓                                                          |
                # ----->                                                          |
                #   |   ↑ pinEndToPinName ↑ maxInNameLen ↑ spaceBetweenBoxNPinName|
                #   |-------------------------------------------------------------|
                self.isInPinExist = False
                self.isOutPinExist = False
                if dirIdx["input"] > 0:
                        self.isInPinExist = True
                if dirIdx["output"] > 0:
                        self.isOutPinExist = True
                # workaround characters are not monospaced, it is very hard to calculate width of the box.
                # if output pin exist I just align edge of the box to output pin and recalculate box width
                # in case there is no output pin, this is going to be used
                if not self.isOutPinExist:
                        self.boxWidth = KiConst.symEdit["lenPin"] - KiConst.symEdit["pinToBoxWidth"] + \
                                        KiConst.symEdit["pinEndToPinName"] + \
                                        (dirMaxNameLen["input"] * KiConst.symEdit["charWidth"]) + \
                                        KiConst.symEdit["spaceBetweenBoxNPinName"]
                #
                # IC1
                # |----------------|   ← pinToBoxHeight
                # |              ----> ← 
                # |                |     heightBetweenPins
                # |              ----> ← 
                # |----------------|   ← pinToBoxHeight
                #
                whoHasMaxPin = "input"
                if dirIdx["output"] > dirIdx["input"]:
                        whoHasMaxPin = "output"
                maxPin = dirIdx[whoHasMaxPin]
                self.boxHeight = ((maxPin-1) * KiConst.symEdit["heightBetweenPins"]) + \
                                 (KiConst.symEdit["pinToBoxHeight"] * 2)

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
                        self.symEditPins[i].prepareForAutoLayout(dirIdx[self.sym.pins[i].dir],
                                                                 dirMaxNameLen)
                        dirIdx[self.sym.pins[i].dir] = dirIdx[self.sym.pins[i].dir] + 1
                self.__calcBoxWidthHeight(dirIdx, dirMaxNameLen)

        def __calcBoxEdges(self):
                #    x0
                #    ↓
                # y0→|-------------------|
                #    |                   |
                #    |                   |
                #    |-------------------|←y1
                #                        ↑
                #                        x1
                if self.isInPinExist:
                        self.x0 = KiConst.symEdit["pinToBoxWidth"]
                else:
                        self.x0 = 0
                self.y0 = -KiConst.symEdit["firstPinyOffset"] + KiConst.symEdit["pinToBoxHeight"]
                # see workaround comment in __calcBoxWidthHeight to understand why boxWidth is recalculated
                if self.isOutPinExist:
                        for i in range(self.sym.numOfPins):
                                if self.sym.pins[i].dir == "output":
                                        self.x1 = self.symEditPins[i].x - KiConst.symEdit["pinToBoxWidth"]
                                        break
                        self.boxWidth = self.x1 - self.x0
                else:
                        self.x1 = self.x0 + self.boxWidth
                self.y1 = self.y0 - self.boxHeight

        def __calcSymbolWidthHeight(self):
                if self.isOutPinExist:
                        self.width = self.x1 + KiConst.symEdit["pinToBoxWidth"]
                else:
                        self.width = self.x1
                self.height = abs(self.y1)

        def autoLayout(self):
                for i in range(self.sym.numOfPins):
                        self.symEditPins[i].autoLayout()

                self.__calcBoxEdges()
                self.__calcSymbolWidthHeight()

        def log(self, depth, pos):
                s = KiUtil.getLogDepthStr(depth, pos) + "SymName: " + self.sym.name +  \
                    " w " + str(self.width) + \
                    " h " + str(self.height) + \
                    " x0 " + str(self.x0) + \
                    " x1 " + str(self.x1) + \
                    " y0 " + str(self.y0) + \
                    " y1 " + str(self.y1) + "\n"
                for i in range(self.sym.numOfPins):
                        s = s + self.symEditPins[i].log(depth + 1, i + 1)
                return s

class KiSymEditLib:
        def __init__(self):
                self.lib = None # KiLib type
                # this one does not have any physical items to be placed
                self.symEditSyms = [] # class _KiSymEditSym type
                self.outFileName = "" # just for debugging purposes

        def __prepareForAutoLayout(self):
                for i in range(self.lib.numOfSymbols):
                        self.symEditSyms[i].prepareForAutoLayout()

        def __autoLayout(self):
                for i in range(self.lib.numOfSymbols):
                        self.symEditSyms[i].autoLayout()

        # KiSymEditLib is suppose to contain data from KiPrj
        # and do auto layout for them
        def parse(self, lib):
                self.lib = lib
                for i in range(lib.numOfSymbols):
                        kiSymEditSym = _KiSymEditSym()
                        kiSymEditSym.parse(lib.symbols[i])
                        self.symEditSyms.append(kiSymEditSym)
                self.__prepareForAutoLayout()
                self.__autoLayout()

        def log(self, depth, pos):
                s = KiUtil.getLogDepthStr(depth, pos) + "LibName: " + self.lib.name + "\n"
                for i in range(self.lib.numOfSymbols):
                        s = s + self.symEditSyms[i].log(depth + 1, i + 1)
                return s

        def gen(self, templateFilePath, outFolderPath):
                templateFileName = os.path.basename(templateFilePath)
                templateLoader = jinja2.FileSystemLoader(searchpath=os.path.dirname(templateFilePath))
                templateEnv = jinja2.Environment(loader=templateLoader)
                template = templateEnv.get_template(templateFileName)

                # change the filename to library name
                self.outFileName = templateFileName.replace(KiConst.invertedUniqDict["xlib.name"], self.lib.name)

                outFilePath = os.path.join(outFolderPath, self.outFileName)
                renderedText = template.render(symEditSyms = self.symEditSyms,
                                               lib = self.lib)
                with open(os.path.join(outFolderPath, outFilePath), 'w') as f:
                        f.write(renderedText)
                print("Gen: " + str(outFilePath))