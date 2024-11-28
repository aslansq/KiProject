# this file is going to be used for autolayout schematic editor

from kiconst import KiConst
from kiutil import KiUtil
import jinja2
import os

class _KiSchEditNode:
        def __init__(self):
                self.node = ""
                self.dir = ""
                self.x = 0
                self.y = 0
                self.idx = 0
                self.dirNodeMaxNameLen = {
                        "input" : 0,
                        "output": 0
                }
        
        def parse(self, node, dir):
                self.node = node
                self.dir = dir

        def prepareForAutoLayout(self, dirNodeMaxNameLen, idx):
                self.dirNodeMaxNameLen = dirNodeMaxNameLen
                self.idx = idx

        def log(self, depth, pos):
                s = KiUtil.getLogDepthStr(depth, pos) + "NodeName: " + self.node + " " + self.dir + " NodeIdx: " + str(self.idx) + "\n"
                return s

class _KiSchEditConn:
        def __init__(self):
                self.x = 0
                self.y = 0
                self.schEditNodes = [] # class _KiSchEditNode type
                self.conn = None
                self.idx = 0
        
        def parse(self, conn):
                self.conn = conn
                for i in range(self.conn.numOfNodes):
                        schEditNode = _KiSchEditNode()
                        schEditNode.parse(self.conn.nodes[i], self.conn.dir)
                        self.schEditNodes.append(schEditNode)

        def prepareForAutoLayout(self, dirNodeMaxNameLen, connIdx):
                self.idx = connIdx
                for i in range(self.conn.numOfNodes):
                        self.schEditNodes[i].prepareForAutoLayout(dirNodeMaxNameLen, i)

        def log(self, depth, pos):
                if self.conn.numOfNodes == 0:
                        return ""
                s = KiUtil.getLogDepthStr(depth, pos) + "ConnName: " + self.conn.name + " ConnIdx: " + str(self.idx) + "\n"
                for i in range(self.conn.numOfNodes):
                        s = s + self.schEditNodes[i].log(depth + 1, i + 1)
                return s

class _KiSchEditPin:
        def __init__(self):
                self.symEditPin = None
                self.schEditConn = _KiSchEditConn()
                self.x = 0
                self.y = 0
        
        def parse(self, symEditPin):
                self.symEditPin = symEditPin
                self.schEditConn.parse(symEditPin.pin.conn)

        def prepareForAutoLayout(self, dirNodeMaxNameLen, connIdx):
                self.schEditConn.prepareForAutoLayout(dirNodeMaxNameLen, connIdx)

        def log(self, depth, pos):
                s = KiUtil.getLogDepthStr(depth, pos) + "PinName: " + self.symEditPin.pin.name + "\n"
                s = s + self.schEditConn.log(depth + 1, 1)
                return s

class _KiSchEditSym:
        def __init__(self):
                self.symEditSym = None
                self.schEditPins = []
                self.libName = ""
        
        def parse(self, libName, symEditSym):
                self.symEditSym = symEditSym
                self.libName = libName
                for i in range(symEditSym.sym.numOfPins):
                        schEditPin = _KiSchEditPin()
                        schEditPin.parse(symEditSym.symEditPins[i])
                        self.schEditPins.append(schEditPin)

        def log(self, depth, pos):
                s = KiUtil.getLogDepthStr(depth, pos) + "LibName: " + self.libName + " SymName: " + self.symEditSym.sym.name + "\n"
                for i in range(self.symEditSym.sym.numOfPins):
                        s = s + self.schEditPins[i].log(depth + 1, i + 1)
                return s

        def prepareForAutoLayout(self):
                dirNodeMaxNameLen = {
                        "input" : 0,
                        "output": 0
                }

                dirConnIdx = {
                        "input" : 0,
                        "output": 0
                }

                for i in range(self.symEditSym.sym.numOfPins):
                        pin = self.symEditSym.sym.pins[i]
                        for j in range(pin.conn.numOfNodes):
                                if len(pin.conn.nodes[j]) > dirNodeMaxNameLen[pin.conn.dir]:
                                        dirNodeMaxNameLen[pin.conn.dir] = len(pin.conn.nodes[j])

                for i in range(self.symEditSym.sym.numOfPins):
                        if self.symEditSym.sym.pins[i].conn.numOfNodes != 0:
                                self.schEditPins[i].prepareForAutoLayout(dirNodeMaxNameLen, dirConnIdx[self.symEditSym.sym.pins[i].dir])
                                dirConnIdx[self.symEditSym.sym.pins[i].dir] = dirConnIdx[self.symEditSym.sym.pins[i].dir] + 1
                        else:
                                self.schEditPins[i].prepareForAutoLayout(dirNodeMaxNameLen, KiConst.schEdit["invalidConnIdx"])

class KiSchEditPrj:
        def __init__(self):
                self.symEditLibs = None # KiSymEditLib type
                self.schEditSyms = []
                self.projectName = ""
                self.numOfSchEditSyms = 0

        def __prepareForAutoLayout(self):
                for i in range(len(self.schEditSyms)):
                        self.schEditSyms[i].prepareForAutoLayout()

        def parse(self, projectName, symEditLibs):
                self.projectName = projectName
                self.symEditLibs = symEditLibs
                for i in range(len(self.symEditLibs)):
                        symEditLib = self.symEditLibs[i]
                        for j in range(len(symEditLib.symEditSyms)):
                                symEditSym = symEditLib.symEditSyms[j] # KiSymEditSym type
                                schEditSym = _KiSchEditSym()
                                schEditSym.parse(symEditLib.lib.name, symEditSym)
                                self.schEditSyms.append(schEditSym)
                self.numOfSchEditSyms = len(self.schEditSyms)
                self.__prepareForAutoLayout()

        def log(self, depth, pos):
                s = KiUtil.getLogDepthStr(depth, pos) + "PrjName: " + self.projectName + "\n"
                for i in range(self.numOfSchEditSyms):
                        s = s + self.schEditSyms[i].log(depth + 1, i + 1)
                return s

        def gen(self, templateFilePath, outFolderPath):
                
                templateFileName = os.path.basename(templateFilePath)
                templateLoader = jinja2.FileSystemLoader(searchpath=os.path.dirname(templateFilePath))
                templateEnv = jinja2.Environment(loader=templateLoader)
                template = templateEnv.get_template(templateFileName)

                # change the filename to library name
                self.outFileName = templateFileName.replace(KiConst.invertedUniqDict["xproject.name"], self.projectName)

                outFilePath = os.path.join(outFolderPath, self.outFileName)
                renderedText = template.render(symEditLibs=self.symEditLibs,
                                               schEditSyms = self.schEditSyms)
                with open(os.path.join(outFolderPath, outFilePath), 'w') as f:
                        f.write(renderedText)
                print("Gen: " + str(outFilePath))
