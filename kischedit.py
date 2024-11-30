# this file is going to be used for autolayout schematic editor

from kiconst import KiConst
from kiutil import KiUtil
import jinja2
import os

class _KiSchEditNode:
        def __init__(self):
                self.x = 0
                self.y = 0
                self.dir = ""
                self.name = ""
                self.idx = 0

        def parse(self, dir, name, idx):
                self.name = name
                self.dir = dir
                self.idx = idx

        def prepareForLayout(self, connWidth):
                self.y = KiConst.schEdit["connyFirstOffset"] + \
                         (KiConst.globalLabel["height"] * self.idx)
                if self.dir == "input":
                        self.x = connWidth
        def autoLayout(self, x, y):
                self.x = self.x + x
                self.y = self.y + y

class _KiSchEditConn:
        def __init__(self):
                self.x = 0
                self.y = 0
                self.dir = ""
                self.name = ""
                self.width = 0
                self.height = 0
                self.schEditNodes = []
                self.schEditNumOfNodes = 0

        def parse(self, name, dir, nodes, idx):
                self.name = name
                self.dir = dir
                self.schEditNumOfNodes = len(nodes)
                for i in range(self.schEditNumOfNodes):
                        schEditNode = _KiSchEditNode()
                        schEditNode.parse(dir, nodes[i], i)
                        self.schEditNodes.append(schEditNode)
                self.idx = idx
        
        # x, y place in conn column
        def prepareForLayout(self, maxNodeNameLenInModule):
                self.height = KiConst.globalLabel["height"] * self.schEditNumOfNodes
                self.width = KiConst.globalLabel["leftToTextWidth"] + \
                             (maxNodeNameLenInModule * KiConst.globalLabel["charWidth"]) + \
                             KiConst.globalLabel["rightToTextWidth"]
                for i in range(self.schEditNumOfNodes):
                        self.schEditNodes[i].prepareForLayout(self.width)
                self.y = KiConst.schEdit["connyGap"] * self.idx

        def autoLayout(self, x, y):
                self.x = self.x + x
                self.y = self.y + y
                for i in range(self.schEditNumOfNodes):
                        self.schEditNodes[i].autoLayout(self.x, self.y)

class _KiSchEditModule:
        def __init__(self):
                self.name = ""
                self.symEditSym = None
                self.libName = ""

                self.schEditConns = {
                        "input" : [],
                        "output" : []
                }

                self.numOfSchEditConns = {
                        "input" : 0,
                        "output" : 0
                }

                self.width = 0
                self.height = 0
                self.symx = 0
                self.symy = 0
                self.desigx = 0
                self.desigy = 0

        def parse(self, libName, symEditSym):
                self.symEditSym = symEditSym
                self.name = symEditSym.sym.name
                self.libName = libName
                connIdx = {
                        "input" : 0,
                        "output" : 0
                }
                # iterate over pins
                for i in range(self.symEditSym.sym.numOfPins):
                        # current pin
                        pin = self.symEditSym.sym.pins[i]
                        # if pins connector have any node, ignore others we do not draw them
                        if pin.conn.numOfNodes != 0:
                                # create schEditConn to layout
                                schEditConn = _KiSchEditConn()
                                # parsing
                                schEditConn.parse(pin.conn.name, pin.dir, pin.conn.nodes, connIdx[pin.dir])
                                # added it modules connectors
                                self.schEditConns[pin.dir].append(schEditConn)
                                connIdx[pin.dir] = connIdx[pin.dir] + 1
                for dir in ["input", "output"]:
                        self.numOfSchEditConns[dir] = len(self.schEditConns[dir])

        def prepareForLayout(self):
                maxNodeNameLen = {
                        "input" : 0,
                        "output" : 0
                }
                for dir in ["input", "output"]:
                        for i in range(self.numOfSchEditConns[dir]):
                                for j in range(self.schEditConns[dir][i].schEditNumOfNodes):
                                        nodeName = self.schEditConns[dir][i].schEditNodes[j].name
                                        if len(nodeName) > maxNodeNameLen[dir]:
                                                maxNodeNameLen[dir] = len(nodeName)

                for dir in ["input", "output"]:
                        for i in range(self.numOfSchEditConns[dir]):
                                self.schEditConns[dir][i].prepareForLayout(maxNodeNameLen[dir])
                
                for dir in ["input", "output"]:
                        maxWidth = 0
                        for i in range(self.numOfSchEditConns[dir]):
                                if self.schEditConns[dir][i].width > maxWidth:
                                        maxWidth = self.schEditConns[dir][i].width
                        if dir == "input":
                                self.symx = maxWidth
                        self.width = self.width + maxWidth
                
                self.width = self.width + self.symEditSym.width

                for dir in ["input", "output"]:
                        totalHeight = 0
                        for i in range(self.numOfSchEditConns[dir]):
                                totalHeight = totalHeight + self.schEditConns[dir][i].height
                                totalHeight = totalHeight + KiConst.schEdit["connyGap"]
                        if totalHeight > self.height:
                                self.height = totalHeight
                
                if self.symEditSym.height > self.height:
                        self.height = self.symEditSym.height

        def autoLayout(self, x, y):
                inConnHeights = 0
                for i in range(self.numOfSchEditConns["input"]):
                        self.schEditConns["input"][i].autoLayout(x, y + inConnHeights)
                        inConnHeights = inConnHeights + self.schEditConns["input"][i].height

                self.symx = self.symx + x
                self.symy = self.symy + y
                self.desigx = self.symx + KiConst.schEdit["desigxOffset"]
                self.desigy = self.symy + KiConst.schEdit["desigyOffset"]
                outConnHeights = 0
                for i in range(self.numOfSchEditConns["output"]):
                        self.schEditConns["output"][i].autoLayout(self.symx + self.symEditSym.width, y + outConnHeights)
                        outConnHeights = outConnHeights + self.schEditConns["output"][i].height


class KiSchEditPrj:
        def __init__(self):
                self.schEditModules = []
                self.projectName = ""
                self.numOfSchEditModules = 0
                self.symEditLibs = []


        def parse(self, projectName, symEditLibs):
                self.symEditLibs = symEditLibs
                self.projectName = projectName
                for i in range(len(symEditLibs)):
                        for j in range(symEditLibs[i].lib.numOfSymbols):
                                symEditSym = symEditLibs[i].symEditSyms[j]
                                schEditModule = _KiSchEditModule()
                                schEditModule.parse(symEditLibs[i].lib.name, symEditSym)
                                self.schEditModules.append(schEditModule)
                self.numOfSchEditModules = len(self.schEditModules)
                for i in range(self.numOfSchEditModules):
                        self.schEditModules[i].prepareForLayout()
                moduleHeights = 0
                for i in range(self.numOfSchEditModules):
                        self.schEditModules[i].autoLayout(0, moduleHeights)
                        moduleHeights = moduleHeights + self.schEditModules[i].height + KiConst.schEdit["moduleyGap"]

        def gen(self, templateFilePath, outFolderPath):
                templateFileName = os.path.basename(templateFilePath)
                templateLoader = jinja2.FileSystemLoader(searchpath=os.path.dirname(templateFilePath))
                templateEnv = jinja2.Environment(loader=templateLoader)
                template = templateEnv.get_template(templateFileName)

                # change the filename to library name
                self.outFileName = templateFileName.replace(KiConst.invertedUniqDict["xproject.name"], self.projectName)

                outFilePath = os.path.join(outFolderPath, self.outFileName)
                renderedText = template.render(symEditLibs=self.symEditLibs,
                                               schEditModules = self.schEditModules)
                with open(os.path.join(outFolderPath, outFilePath), 'w') as f:
                        f.write(renderedText)
                print("Gen: " + str(outFilePath))
