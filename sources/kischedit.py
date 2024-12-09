# this file is going to be used for autolayout schematic editor

from kiconst import KiConst
from kiutil import KiUtil
import jinja2
import os

class _KiSchEditNode:
        def __init__(self):
                self.x = 0
                self.y = 0
                self.pos = ""
                self.name = ""
                self.idx = 0
                self.type = ""

        def parse(self, pos, name, idx, type):
                self.name = name
                self.pos = pos
                self.idx = idx
                self.type = type

        def prepareForLayout(self, connWidth):
                self.y = KiConst.schEdit["connyFirstOffset"] + \
                         (KiConst.globalLabel["height"] * self.idx)
                if self.pos == "left":
                        self.x = connWidth
        def autoLayout(self, x, y):
                self.x = self.x + x
                self.y = self.y + y

class _KiSchEditConn:
        def __init__(self):
                self.x = 0
                self.y = 0
                self.pos = ""
                self.name = ""
                self.width = 0
                self.height = 0
                self.schEditNodes = []
                self.schEditNumOfNodes = 0
                self.idx = 0

        def parse(self, pin, idx):
                self.name = pin.conn.name
                self.pos = pin.pos
                nodes = pin.conn.nodes
                self.schEditNumOfNodes = len(nodes)
                for i in range(self.schEditNumOfNodes):
                        schEditNode = _KiSchEditNode()
                        schEditNode.parse(self.pos, nodes[i], i, pin.type)
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
        def __init__(self, name):
                self.x0 = 0
                self.x1 = 0
                self.y0 = 0
                self.y1 = 0
                self.len = 0
                self.o = '' # v(vertical) or h(horizontal)
                self.name = name

        def prepareForLayout(self, x, y, o, len):
                self.x0 = x
                self.y0 = y
                self.o = o
                self.len = len
                if self.o != 'v' and self.o != 'h':
                        raise Exception("ERROR undefined orientation.")
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

        def custom(self, x0, y0, x1, y1):
                self.x0 = x0
                self.y0 = y0
                self.x1 = x1
                self.y1 = y1

class _KiSchEditWireCont:
        def __init__(self):
                self.width = 0
                self.schEditConns = None
                self.numOfSchEditConns = 0
                self.wires = [] # _KiSchEditWire
                self.pos = ""
                self.x = 0
                self.y = 0
                self.endPoints = [
                # {
                # "connName"
                # "x"
                # "y"
                # }
                ]
                self.numOfEndPoints = 0
                self.connWMultipleNodesExist = False

        def parse(self, schEditConns):
                self.schEditConns = schEditConns
                self.numOfSchEditConns = len(self.schEditConns)
                self.pos = self.schEditConns[0].pos
                for i in range(self.numOfSchEditConns):
                        if self.schEditConns[i].schEditNumOfNodes > 1:
                                self.connWMultipleNodesExist = True
                                break

        def __prepareInWireMultiNode(self, schEditConn, totalNode):
                #-----------------------------------------------------------
                #            NodeToConnVerticalWire
                #            ↓   ↓
                # |----------|   
                # ||-------\ |    
                # ||        >|---|
                # ||-------/ |   |    ↓
                # ||-------\ |   |---← endPoint
                # ||        >|---|
                # ||-------/ |    
                # |----------|    
                #                ↑
                #                ConnVerticalWire

                # Begin NodeToConnVerticalWire
                for j in range(schEditConn.schEditNumOfNodes):
                        schEditNode = schEditConn.schEditNodes[j]
                        wire = _KiSchEditWire("NodeToConnVerticalWire_" + schEditNode.name)
                        x = 0
                        y = (schEditConn.idx * KiConst.schEdit["connyGap"]) + \
                        (KiConst.globalLabel["height"] * (schEditNode.idx + totalNode)) + \
                        (KiConst.globalLabel["height"] / 2)
                        wire.prepareForLayout(x, y, 'h', KiConst.schEdit["wirexGap"])
                        self.wires.append(wire)
                # End NodeToConnVerticalWire

                # Begin ConnVerticalWire
                wire = _KiSchEditWire("ConnVerticalWire_"+schEditConn.name)
                x = KiConst.schEdit["wirexGap"]
                y = (schEditConn.idx * KiConst.schEdit["connyGap"]) + \
                (KiConst.globalLabel["height"] * (schEditConn.schEditNodes[0].idx + totalNode)) + \
                (KiConst.globalLabel["height"] / 2)
                len = (schEditConn.schEditNumOfNodes - 1) * KiConst.globalLabel["height"]
                wire.prepareForLayout(x, y, 'v', len)
                self.wires.append(wire)
                # End ConnVerticalWire

                wire = _KiSchEditWire("Endpoint_"+schEditConn.name)
                y = y + len/2
                len = KiConst.schEdit["wirexGap"]
                wire.prepareForLayout(x, y, 'h', len)
                self.wires.append(wire)

                endPoint = {
                        "name" : schEditConn.name,
                        "x" : x + len,
                        "y" : y
                }
                self.endPoints.append(endPoint)
        def __prepareWireSingleNode(self, schEditConn, totalNode):
                # right
                #-----------------------------------------------------------
                #             |----------|
                # endpoint↓   ||-------\ |
                #         →---||        >|←
                #             ||-------/ |
                #             |----------|
                #
                # left
                #-----------------------------------------------------------
                # |----------|   
                # ||-------\ |   ↓endPoint
                # ||        >|---←
                # ||-------/ |
                # |----------|
                #             
                schEditNode = schEditConn.schEditNodes[0]
                len = KiConst.schEdit["wirexGap"]
                if self.connWMultipleNodesExist:
                        len = len + KiConst.schEdit["wirexGap"]
                if self.pos == "left":
                        x = 0
                elif self.pos == "right":
                        x = self.width - len
                y = (schEditConn.idx * KiConst.schEdit["connyGap"]) + \
                    (KiConst.globalLabel["height"] * (schEditNode.idx + totalNode)) + \
                    (KiConst.globalLabel["height"] / 2)

                wire = _KiSchEditWire("Endpoint_" + schEditNode.name)
                wire.prepareForLayout(x, y, 'h', len)
                self.wires.append(wire)

                if self.pos == "left":
                        x = x + len

                endPoint = {
                        "name" : schEditConn.name,
                        "x" : x,
                        "y" : y
                }
                self.endPoints.append(endPoint)

        def __prepareWireContainer(self):
                totalNode = 0
                for i in range(self.numOfSchEditConns):
                        schEditConn = self.schEditConns[i]
                        multiNode = schEditConn.schEditNumOfNodes > 1
                        if multiNode and self.pos == "right":
                                raise Exception("ERROR OUTPUT conn container can NOT have multiple nodes")
                        elif schEditConn.schEditNumOfNodes > 1:
                                self.__prepareInWireMultiNode(schEditConn, totalNode)
                        else:
                                self.__prepareWireSingleNode(schEditConn, totalNode)
                        totalNode = totalNode + schEditConn.schEditNumOfNodes
                self.numOfEndPoints = len(self.endPoints)


        def prepareForLayout(self):
                if self.connWMultipleNodesExist:
                        self.width = KiConst.schEdit["wirexGap"] * 6
                else:
                        self.width = KiConst.schEdit["wirexGap"] * 4
                self.__prepareWireContainer()

        def autoLayout(self, x, y):
                self.x = x
                self.y = y
                for i in range(len(self.wires)):
                        self.wires[i].autoLayout(x, y)
                for i in range(self.numOfEndPoints):
                        self.endPoints[i]["x"] = self.endPoints[i]["x"] + x
                        self.endPoints[i]["y"] = self.endPoints[i]["y"] + y

class _KiSchEditModule:
        def __init__(self):
                self.name = ""
                self.symEditSym = None
                self.libName = ""

                self.schEditConns = {
                        "left" : [],
                        "right" : []
                }

                self.schEditConnsHeight = {
                        "left" : 0,
                        "right" : 0
                }

                self.numOfSchEditConns = {
                        "left" : 0,
                        "right" : 0
                }

                self.schEditWireCont = {
                        "left": None,
                        "right": None
                }

                self.width = 0
                self.height = 0
                self.symx = 0
                self.symy = 0
                self.desigx = 0
                self.desigy = 0

                self.finalWires = []
                self.numOfFinalWires = 0

        def parse(self, libName, symEditSym):
                self.symEditSym = symEditSym
                self.name = symEditSym.sym.name
                self.libName = libName
                connIdx = {
                        "left" : 0,
                        "right" : 0
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
                                schEditConn.parse(pin, connIdx[pin.pos])
                                # added it modules connectors
                                self.schEditConns[pin.pos].append(schEditConn)
                                connIdx[pin.pos] = connIdx[pin.pos] + 1
                for pos in ["left", "right"]:
                        self.numOfSchEditConns[pos] = len(self.schEditConns[pos])
                
                for pos in ["left", "right"]:
                        if self.numOfSchEditConns[pos] != 0:
                                self.schEditWireCont[pos] = _KiSchEditWireCont()
                                self.schEditWireCont[pos].parse(self.schEditConns[pos])

        def prepareForLayout(self):
                maxNodeNameLen = {
                        "left" : 0,
                        "right" : 0
                }
                for pos in ["left", "right"]:
                        for i in range(self.numOfSchEditConns[pos]):
                                for j in range(self.schEditConns[pos][i].schEditNumOfNodes):
                                        nodeName = self.schEditConns[pos][i].schEditNodes[j].name
                                        if len(nodeName) > maxNodeNameLen[pos]:
                                                maxNodeNameLen[pos] = len(nodeName)

                for pos in ["left", "right"]:
                        for i in range(self.numOfSchEditConns[pos]):
                                self.schEditConns[pos][i].prepareForLayout(maxNodeNameLen[pos])
                
                for pos in ["left", "right"]:
                        maxWidth = 0
                        for i in range(self.numOfSchEditConns[pos]):
                                if self.schEditConns[pos][i].width > maxWidth:
                                        maxWidth = self.schEditConns[pos][i].width
                        self.width = self.width + maxWidth


                for pos in ["left", "right"]:
                        if self.numOfSchEditConns[pos] != 0:
                                self.schEditWireCont[pos].prepareForLayout()
                                self.width = self.width + self.schEditWireCont[pos].width
                                
                self.width = self.width + self.symEditSym.width

                for pos in ["left", "right"]:
                        totalHeight = 0
                        for i in range(self.numOfSchEditConns[pos]):
                                totalHeight = totalHeight + self.schEditConns[pos][i].height
                                if i != (self.numOfSchEditConns[pos]-1):
                                        totalHeight = totalHeight + KiConst.schEdit["connyGap"]
                        if totalHeight > self.height:
                                self.height = totalHeight
                        self.schEditConnsHeight[pos] = totalHeight
                
                if self.symEditSym.height > self.height:
                        self.height = self.symEditSym.height

        def __connectConnToSymbol(self):
                for pos in ["left", "right"]:
                        if self.numOfSchEditConns[pos] != 0:
                                for i in range(self.symEditSym.sym.numOfPins):
                                        symEditPin = self.symEditSym.symEditPins[i]
                                        for j in range(self.schEditWireCont[pos].numOfEndPoints):
                                                endPoint = self.schEditWireCont[pos].endPoints[j]
                                                if endPoint["name"] == symEditPin.pin.conn.name:
                                                        wire = _KiSchEditWire("Final_" + symEditPin.pin.conn.name)
                                                        wire.custom(endPoint["x"],
                                                                endPoint["y"],
                                                                symEditPin.x + self.symx,
                                                                abs(symEditPin.y) + self.symy)
                                                        self.finalWires.append(wire)
                self.numOfFinalWires = len(self.finalWires)

        def autoLayout(self, x, y):
                inConnyOffset = 0
                if self.height > self.schEditConnsHeight["left"]:
                        inConnyOffset = (self.height - self.schEditConnsHeight["left"]) / 2
                        inConnyOffset = KiUtil.roundToGrid(inConnyOffset)

                for i in range(self.numOfSchEditConns["left"]):
                        self.schEditConns["left"][i].autoLayout(x, y + inConnyOffset)
                        inConnyOffset = inConnyOffset + self.schEditConns["left"][i].height

                if self.numOfSchEditConns["left"] != 0:
                        self.schEditWireCont["left"].autoLayout(self.schEditConns["left"][0].x + \
                                                                 self.schEditConns["left"][0].width, self.schEditConns["left"][0].y)

                # if there is input connectors there is also wires
                if self.numOfSchEditConns["left"] != 0:
                        self.symx = self.schEditWireCont["left"].x + self.schEditWireCont["left"].width
                else:
                        self.symx = x

                self.symy = y + (self.height-self.symEditSym.height) / 2 - KiConst.symEdit["charHeight"]
                self.symx = KiUtil.roundToGrid(self.symx)
                self.symy = KiUtil.roundToGrid(self.symy)

                self.desigx = self.symx + KiConst.schEdit["desigxOffset"]
                self.desigy = self.symy + KiConst.schEdit["desigyOffset"]

                outConnyOffset = 0
                if self.height > self.schEditConnsHeight["right"]:
                        outConnyOffset = (self.height - self.schEditConnsHeight["right"]) / 2
                        outConnyOffset = KiUtil.roundToGrid(outConnyOffset)

                if self.numOfSchEditConns["right"] != 0:
                        self.schEditWireCont["right"].autoLayout(self.symx + self.symEditSym.width, y + outConnyOffset)

                for i in range(self.numOfSchEditConns["right"]):
                        self.schEditConns["right"][i].autoLayout(self.schEditWireCont["right"].x + \
                                                                  self.schEditWireCont["right"].width, y + outConnyOffset)
                        outConnyOffset = outConnyOffset + self.schEditConns["right"][i].height

                self.__connectConnToSymbol()


class KiSchEditPrj:
        def __init__(self, logFolderPath, showPinNumbers):
                self.schEditModules = []
                self.projectName = ""
                self.numOfSchEditModules = 0
                self.symEditLibs = []
                self.pageWidth = 0
                self.pageHeight = 0
                self.logFolderPath = logFolderPath
                self.showPinNumbers = showPinNumbers

        def parse(self, projectName, symEditLibs, pageWidth, pageHeight):
                self.symEditLibs = symEditLibs
                self.projectName = projectName
                self.pageHeight = pageHeight
                self.pageWidth = pageWidth
                for i in range(len(symEditLibs)):
                        for j in range(symEditLibs[i].lib.numOfSymbols):
                                symEditSym = symEditLibs[i].symEditSyms[j]
                                schEditModule = _KiSchEditModule()
                                schEditModule.parse(symEditLibs[i].lib.name, symEditSym)
                                self.schEditModules.append(schEditModule)
                self.numOfSchEditModules = len(self.schEditModules)
                for i in range(self.numOfSchEditModules):
                        self.schEditModules[i].prepareForLayout()
                modulexOffset = 0
                moduleyOffset = 0
                maxWidth = 0
                for i in range(self.numOfSchEditModules):
                        if moduleyOffset + self.schEditModules[i].height < self.pageHeight:
                                self.schEditModules[i].autoLayout(modulexOffset, moduleyOffset)
                                if self.schEditModules[i].width > maxWidth:
                                        maxWidth = self.schEditModules[i].width
                        else:
                                modulexOffset = modulexOffset + maxWidth + KiConst.schEdit["modulexGap"]
                                moduleyOffset = 0
                                maxWidth = self.schEditModules[i].width
                                self.schEditModules[i].autoLayout(modulexOffset, moduleyOffset)
                        moduleyOffset = moduleyOffset + self.schEditModules[i].height + KiConst.schEdit["moduleyGap"]

                if modulexOffset + maxWidth > self.pageWidth:
                        return False
                return True

        def gen(self, templateFilePath, outFolderPath):
                templateFileName = os.path.basename(templateFilePath)
                templateLoader = jinja2.FileSystemLoader(searchpath=os.path.dirname(templateFilePath))
                templateEnv = jinja2.Environment(loader=templateLoader)
                template = templateEnv.get_template(templateFileName)

                # change the filename to library name
                self.outFileName = templateFileName.replace(KiConst.invertedUniqDict["xproject.name"], self.projectName)

                outFilePath = os.path.join(outFolderPath, self.outFileName)
                renderedText = template.render(symEditLibs=self.symEditLibs,
                                               schEditModules = self.schEditModules,
                                               pageWidth=self.pageWidth,
                                               pageHeight=self.pageHeight,
                                               showPinNumbers=self.showPinNumbers,
                                               loggingEnabled=False)
                with open(outFilePath, 'w') as f:
                        f.write(renderedText)

                outFolderPath = os.path.join(self.logFolderPath, self.projectName)
                if not os.path.exists(outFolderPath):
                        os.makedirs(outFolderPath)
                outFilePath = os.path.join(outFolderPath, "KiSchEdit_" + self.outFileName)
                renderedText = template.render(symEditLibs=self.symEditLibs,
                                               schEditModules = self.schEditModules,
                                               pageWidth=self.pageWidth,
                                               pageHeight=self.pageHeight,
                                               loggingEnabled=True,
                                               showPinNumbers=self.showPinNumbers)
                with open(outFilePath, 'w') as f:
                        f.write(renderedText)
                print("Gen: " + str(outFilePath))
