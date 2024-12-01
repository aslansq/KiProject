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
                self.idx = 0

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

class _KiSchEditWire:
        def __init__(self):
                self.x0 = 0
                self.x1 = 0
                self.y0 = 0
                self.y1 = 0
                self.len = 0
                self.o = '' # v(vertical) or h(horizontal)

        def prepareForLayout(self, x, y, o, len):
                self.x0 = x
                self.y0 = y
                self.o = o
                self.len = len
                if self.o != 'v' and self.o != 'h':
                        print("ERROR undefined orientation.")
                        exit(1)
                if self.o == 'v':
                        self.x1 = self.x0
                        self.y1 = self.y0 + self.len
                elif self.o == 'h':
                        self.x1 = self.x0 + self.len
                        self.y1 = self.y0
        def autoLayout(self, x, y):
                self.x0 = self.x0 + x
                self.y0 = self.y0 + y
                self.x1 = self.x1 + x
                self.y1 = self.y1 + y

class _KiSchEditWireCont:
        def __init__(self):
                self.width = 0
                self.schEditConns = None
                self.numOfSchEditConns = 0
                self.wires = [] # _KiSchEditWire
                self.dir = ""
                self.x = 0
                self.y = 0
                self.endPoints = [
                # {
                # "connName"
                # "x"
                # "y"
                # }
                ]

        def parse(self, schEditConns):
                self.schEditConns = schEditConns
                self.numOfSchEditConns = len(self.schEditConns)
                self.dir = self.schEditConns[0].dir

        def __prepareInWireMultiNode(self, schEditConn, totalNode):
                #-----------------------------------------------------------
                #            NodeToConnVerticalWire
                #            ↓   ↓
                # |----------|   
                # ||-------\ |    
                # ||        >|---|
                # ||-------/ |   |↓ endPoint
                # ||-------\ |   |←
                # ||        >|---|
                # ||-------/ |    
                # |----------|    
                #                ↑
                #                ConnVerticalWire

                # Begin NodeToConnVerticalWire
                for j in range(schEditConn.schEditNumOfNodes):
                        schEditNode = schEditConn.schEditNodes[j]
                        wire = _KiSchEditWire()
                        x = 0
                        y = (schEditConn.idx * KiConst.schEdit["connyGap"]) + \
                        (KiConst.globalLabel["height"] * (schEditNode.idx + totalNode)) + \
                        (KiConst.globalLabel["height"] / 2)
                        wire.prepareForLayout(x, y, 'h', KiConst.schEdit["wirexGap"])
                        self.wires.append(wire)
                # End NodeToConnVerticalWire

                # Begin ConnVerticalWire
                wire = _KiSchEditWire()
                x = KiConst.schEdit["wirexGap"]
                y = (schEditConn.idx * KiConst.schEdit["connyGap"]) + \
                (KiConst.globalLabel["height"] * (schEditConn.schEditNodes[0].idx + totalNode)) + \
                (KiConst.globalLabel["height"] / 2)
                len = (schEditConn.schEditNumOfNodes - 1) * KiConst.globalLabel["height"]
                wire.prepareForLayout(x, y, 'v', len)
                self.wires.append(wire)
                # End ConnVerticalWire

                endPoint = {
                        "name" : schEditConn.name,
                        "x" : x,
                        "y" : y + len/2
                }
                self.endPoints.append(endPoint)
        def __prepareWireSingleNode(self, schEditConn, totalNode):
                # output
                #-----------------------------------------------------------
                #          |----------|
                # endpoint↓||-------\ |
                #         →||        >|←
                #          ||-------/ |
                #          |----------|
                #
                # input
                #-----------------------------------------------------------
                # |----------|   
                # ||-------\ |↓endPoint
                # ||        >|←
                # ||-------/ |
                # |----------|
                #             
                schEditNode = schEditConn.schEditNodes[0]
                if self.dir == "input":
                        x = 0
                elif self.dir == "output":
                        x = self.width
                y = (schEditConn.idx * KiConst.schEdit["connyGap"]) + \
                    (KiConst.globalLabel["height"] * (schEditNode.idx + totalNode)) + \
                    (KiConst.globalLabel["height"] / 2)
                endPoint = {
                        "name" : schEditConn.name,
                        "x" : x,
                        "y" : y
                }
                self.endPoints.append(endPoint)

        def __prepareInWireContainer(self):
                totalNode = 0
                for i in range(self.numOfSchEditConns):
                        schEditConn = self.schEditConns[i]
                        multiNode = schEditConn.schEditNumOfNodes > 1
                        if multiNode and self.dir == "output":
                                print("ERROR OUTPUT conn container can NOT have multiple nodes")
                                exit(1)
                        elif schEditConn.schEditNumOfNodes > 1:
                                self.__prepareInWireMultiNode(schEditConn, totalNode)
                        else:
                                self.__prepareWireSingleNode(schEditConn, totalNode)
                        totalNode = totalNode + schEditConn.schEditNumOfNodes


        def prepareForLayout(self):
                connWMultipleNodesExist = False
                for i in range(self.numOfSchEditConns):
                        if self.schEditConns[i].schEditNumOfNodes > 1:
                                connWMultipleNodesExist = True
                                break
                self.width = self.numOfSchEditConns * (KiConst.schEdit["wirexGap"] * 2)
                if connWMultipleNodesExist:
                        self.width = self.width + (KiConst.schEdit["wirexGap"] * 2)
                self.__prepareInWireContainer()

        def autoLayout(self, x, y):
                self.x = x
                self.y = y
                for i in range(len(self.wires)):
                        self.wires[i].autoLayout(x, y)

class _KiSchEditModule:
        def __init__(self):
                self.name = ""
                self.symEditSym = None
                self.libName = ""

                self.schEditConns = {
                        "input" : [],
                        "output" : []
                }

                self.schEditConnsHeight = {
                        "input" : 0,
                        "output" : 0
                }

                self.numOfSchEditConns = {
                        "input" : 0,
                        "output" : 0
                }

                self.schEditWireCont = {
                        "input": None,
                        "output": None
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
                
                for dir in ["input", "output"]:
                        if self.numOfSchEditConns[dir] != 0:
                                self.schEditWireCont[dir] = _KiSchEditWireCont()
                                self.schEditWireCont[dir].parse(self.schEditConns[dir])

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
                        self.width = self.width + maxWidth


                for dir in ["input", "output"]:
                        if self.numOfSchEditConns[dir] != 0:
                                self.schEditWireCont[dir].prepareForLayout()
                                self.width = self.width + self.schEditWireCont[dir].width
                                
                self.width = self.width + self.symEditSym.width

                for dir in ["input", "output"]:
                        totalHeight = 0
                        for i in range(self.numOfSchEditConns[dir]):
                                totalHeight = totalHeight + self.schEditConns[dir][i].height
                                if i != (self.numOfSchEditConns[dir]-1):
                                        totalHeight = totalHeight + KiConst.schEdit["connyGap"]
                        if totalHeight > self.height:
                                self.height = totalHeight
                        self.schEditConnsHeight[dir] = totalHeight
                
                if self.symEditSym.height > self.height:
                        self.height = self.symEditSym.height

        def autoLayout(self, x, y):
                inConnyOffset = 0
                if self.height > self.schEditConnsHeight["input"]:
                        inConnyOffset = (self.height - self.schEditConnsHeight["input"]) / 2

                for i in range(self.numOfSchEditConns["input"]):
                        self.schEditConns["input"][i].autoLayout(x, y + inConnyOffset)
                        inConnyOffset = inConnyOffset + self.schEditConns["input"][i].height

                if self.numOfSchEditConns["input"] != 0:
                        self.schEditWireCont["input"].autoLayout(self.schEditConns["input"][0].x + \
                                                                 self.schEditConns["input"][0].width, self.schEditConns["input"][0].y)

                # if there is input connectors there is also wires
                if self.numOfSchEditConns["input"] != 0:
                        self.symx = self.schEditWireCont["input"].x + self.schEditWireCont["input"].width
                else:
                        self.symx = x

                self.symy = y + (self.height-self.symEditSym.height) / 2 - KiConst.symEdit["charHeight"]

                self.desigx = self.symx + KiConst.schEdit["desigxOffset"]
                self.desigy = self.symy + KiConst.schEdit["desigyOffset"]

                if self.numOfSchEditConns["output"] != 0:
                        self.schEditWireCont["output"].autoLayout(self.symx + self.symEditSym.width, y)

                outConnyOffset = 0
                if self.height > self.schEditConnsHeight["output"]:
                        outConnyOffset = (self.height - self.schEditConnsHeight["output"]) / 2

                for i in range(self.numOfSchEditConns["output"]):
                        self.schEditConns["output"][i].autoLayout(self.schEditWireCont["output"].x + \
                                                                  self.schEditWireCont["output"].width, y + outConnyOffset)
                        outConnyOffset = outConnyOffset + self.schEditConns["output"][i].height


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
