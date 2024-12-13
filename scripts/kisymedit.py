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
                # rotation degree
                self.deg = 0
                # positional index
                self.posIdx = 0
                # storing copy in every pin is not needed but it makes things very easy
                self.posMaxNameLenAll = {
                        "left" : 0,
                        "right": 0
                }
        def parse(self, pin):
                self.pin = pin
        
        def prepareForAutoLayout(self, posIdx, posMaxNameLenAll):
                self.posIdx = posIdx
                self.posMaxNameLenAll = posMaxNameLenAll

        def autoLayout(self):
                if self.posIdx == 0: # first one
                        self.y = -KiConst.symEdit["firstPinyOffset"]
                else:
                        self.y = -KiConst.symEdit["firstPinyOffset"] # first pin positions
                        self.y = self.y - (self.posIdx * KiConst.symEdit["heightBetweenPins"])

                # see KiConst.symEdit comment to understand this
                if self.pin.pos == "right":
                        self.deg = 180
                        isLeftPinExist = False
                        if self.posMaxNameLenAll["left"] != 0:
                                isLeftPinExist = True
                        if isLeftPinExist:
                                self.x = self.x + KiConst.symEdit["lenPin"] + \
                                         KiConst.symEdit["pinEndToPinName"] + \
                                         (self.posMaxNameLenAll["left"] * KiConst.symEdit["charWidth"]) + \
                                         KiConst.symEdit["spaceBetweenInNOutPin"]
                        else:
                                self.x = self.x + KiConst.symEdit["spaceBetweenBoxNPinName"]
                        self.x = self.x + \
                                (self.posMaxNameLenAll["right"] * KiConst.symEdit["charWidth"]) + \
                                KiConst.symEdit["pinEndToPinName"] + \
                                KiConst.symEdit["lenPin"]

        def log(self, depth, pos):
                s = KiUtil.getLogDepthStr(depth, pos) + "PinName: " + self.pin.name + " x " + str(self.x) + " y " + str(self.y) 
                s = s + " deg " + str(self.deg) + " posIdx " + str(self.posIdx) + " pos " + self.pin.pos + "\n"
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
                self.isLeftPinExist = False
                self.isRightPinExist = False

        def parse(self, sym):
                self.sym = sym
                for i in range(sym.numOfPins):
                        kiSymEditPin = _KiSymEditPin()
                        kiSymEditPin.parse(sym.pins[i])
                        self.symEditPins.append(kiSymEditPin)

        def __calcBoxWidthHeight(self, posIdx, posMaxNameLen):
                #       |-------------------------------------------------------------|
                #       |                                                             |
                #       |                                                             |
                # ----->|                                                             |
                #       ↑  pinEndToPinName  ↑  maxInNameLen  ↑ spaceBetweenBoxNPinName|
                #       |-------------------------------------------------------------|
                self.isLeftPinExist = False
                self.isRightPinExist = False
                if posIdx["left"] > 0:
                        self.isLeftPinExist = True
                if posIdx["right"] > 0:
                        self.isRightPinExist = True
                # workaround characters are not monospaced, it is very hard to calculate width of the box.
                # if output pin exist I just align edge of the box to output pin and recalculate box width
                # in case there is no output pin, this is going to be used
                if not self.isRightPinExist:
                        self.boxWidth = KiConst.symEdit["pinEndToPinName"] + \
                                        (posMaxNameLen["left"] * KiConst.symEdit["charWidth"]) + \
                                        KiConst.symEdit["spaceBetweenBoxNPinName"]
                #
                # IC1
                # |----------------|      ← pinToBoxHeight
                # |                |----> ← 
                # |                |     heightBetweenPins
                # |                |----> ← 
                # |----------------|      ← pinToBoxHeight
                #
                whoHasMaxPin = "left"
                if posIdx["right"] > posIdx["left"]:
                        whoHasMaxPin = "right"
                maxPin = posIdx[whoHasMaxPin]
                self.boxHeight = ((maxPin-1) * KiConst.symEdit["heightBetweenPins"]) + \
                                 (KiConst.symEdit["pinToBoxHeight"] * 2)

        def __getPosMaxNameLen(self):
                posMaxNameLen = {
                        "left" : 0,
                        "right": 0
                }
                for i in range(self.sym.numOfPins):
                        nameLen = len(self.sym.pins[i].name)
                        if nameLen > posMaxNameLen[self.sym.pins[i].pos]:
                                posMaxNameLen[self.sym.pins[i].pos] = nameLen
                return posMaxNameLen

        def prepareForAutoLayout(self):
                posIdx = {
                        "left"  : 0,
                        "right" : 0
                }
                posMaxNameLen = self.__getPosMaxNameLen()

                for i in range(self.sym.numOfPins):
                        self.symEditPins[i].prepareForAutoLayout(posIdx[self.sym.pins[i].pos],
                                                                 posMaxNameLen)
                        posIdx[self.sym.pins[i].pos] = posIdx[self.sym.pins[i].pos] + 1
                self.__calcBoxWidthHeight(posIdx, posMaxNameLen)

        def __calcBoxEdges(self):
                #    x0
                #    ↓
                # y0→|-------------------|
                #    |                   |
                #    |                   |
                #    |-------------------|←y1
                #                        ↑
                #                        x1
                if self.isLeftPinExist:
                        self.x0 = KiConst.symEdit["lenPin"]
                else:
                        self.x0 = 0
                self.y0 = -KiConst.symEdit["firstPinyOffset"] + KiConst.symEdit["pinToBoxHeight"]
                # see workaround comment in __calcBoxWidthHeight to understand why boxWidth is recalculated
                if self.isRightPinExist:
                        for i in range(self.sym.numOfPins):
                                if self.sym.pins[i].pos == "right":
                                        self.x1 = self.symEditPins[i].x - KiConst.symEdit["lenPin"]
                                        break
                        self.boxWidth = self.x1 - self.x0
                else:
                        self.x1 = self.x0 + self.boxWidth
                self.y1 = self.y0 - self.boxHeight

        def __calcSymbolWidthHeight(self):
                if self.isRightPinExist:
                        self.width = self.x1 + KiConst.symEdit["lenPin"]
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
        def __init__(self, logFolderPath, showPinNumbers):
                self.lib = None # KiLib type
                # this one does not have any physical items to be placed
                self.symEditSyms = [] # class _KiSymEditSym type
                self.outFileName = "" # just for debugging purposes
                self.projectName = ""
                self.logFolderPath = logFolderPath
                self.showPinNumbers = showPinNumbers

        def __prepareForAutoLayout(self):
                for i in range(self.lib.numOfSymbols):
                        self.symEditSyms[i].prepareForAutoLayout()

        def __autoLayout(self):
                for i in range(self.lib.numOfSymbols):
                        self.symEditSyms[i].autoLayout()

        # KiSymEditLib is suppose to contain data from KiPrj
        # and do auto layout for them
        def parse(self, projectName, lib):
                self.projectName = projectName
                self.lib = lib
                for i in range(lib.numOfSymbols):
                        kiSymEditSym = _KiSymEditSym()
                        kiSymEditSym.parse(lib.symbols[i])
                        self.symEditSyms.append(kiSymEditSym)
                self.__prepareForAutoLayout()
                self.__autoLayout()

        def __log(self):
                depth = 0
                pos = 1
                s = KiUtil.getLogDepthStr(depth, pos) + "LibName: " + self.lib.name + "\n"
                for i in range(self.lib.numOfSymbols):
                        s = s + self.symEditSyms[i].log(depth + 1, i + 1)

                absOutFolderPath = os.path.join(self.logFolderPath, self.projectName)
                if not os.path.exists(absOutFolderPath):
                        os.makedirs(absOutFolderPath)
                absOutFilePath = os.path.join(absOutFolderPath, "KiSymEdit_" + self.lib.name + ".txt")
                with open(absOutFilePath, 'w') as f:
                        f.write(s)

        def gen(self, templateFilePath, outFolderPath):
                templateFileName = os.path.basename(templateFilePath)
                templateLoader = jinja2.FileSystemLoader(searchpath=os.path.dirname(templateFilePath))
                templateEnv = jinja2.Environment(loader=templateLoader)
                template = templateEnv.get_template(templateFileName)

                # change the filename to library name
                self.outFileName = templateFileName.replace(KiConst.invertedUniqDict["xlib.name"], self.lib.name)

                outFilePath = os.path.join(outFolderPath, self.outFileName)
                renderedText = template.render(symEditSyms = self.symEditSyms,
                                               lib = self.lib,
                                               showPinNumbers=self.showPinNumbers)
                with open(os.path.join(outFolderPath, outFilePath), 'w') as f:
                        f.write(renderedText)
                print("Gen: " + str(outFilePath))
                self.__log()