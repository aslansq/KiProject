# this file is going to be used for autolayout schematic editor
# sometimes it may seem information unnecessarily copied to other classes, reasoning:
# ease of debugging
# ease of accessing in templates

from kiconst import KiConst
from kiutil import KiUtil
import jinja2
import os

# this is a data structure for a global label
class _KiSchEditNode:
        def __init__(self):
                # x and y are locations in schematic editor
                self.x = 0
                self.y = 0
                self.pos = ""
                self.name = ""
                self.idx = 0
                self.type = ""
                self.uuid = ""

        def parse(self, parentUuid, pos, name, idx, type):
                self.name = name
                self.pos = pos
                self.idx = idx
                self.type = type
                self.uuid = KiUtil.getUuid("_KiSchEditNode" +
                                           parentUuid +
                                           self.name +
                                           str(self.idx))

        def prepareForLayout(self, connWidth):
                # x and y are offseted to their relatives connectors
                # see KiConst.schEdit text art
                
                # this is same for leftConn and rightConn
                self.y = KiConst.schEdit["connyFirstOffset"] + \
                         (KiConst.globalLabel["height"] * self.idx)
                # for left connector
                # all global labes aligned to connWidth
                # connWidth is basically calculated by looking at longest global label name
                if self.pos == "left":
                        self.x = connWidth
        def autoLayout(self, x, y):
                # x and y are offseted in a page in schematic editor
                self.x = self.x + x
                self.y = self.y + y

# data structure for connector
# a connector contains global labels(KiSchEditNode type)
class _KiSchEditConn:
        def __init__(self):
                # x and y are locations in schematic editor
                self.x = 0
                self.y = 0
                self.pos = ""
                self.name = ""
                self.width = 0
                self.height = 0
                # this is just global labes with location values
                self.schEditNodes = [] # _KiSchEditNode
                self.schEditNumOfNodes = 0
                self.idx = 0
                self.uuid = ""

        def parse(self, pin, idx):
                # copy pasting information
                # just to create new re-presentation
                self.name = pin.conn.name
                self.uuid = pin.conn.uuid
                self.pos = pin.pos
                nodes = pin.conn.nodes
                self.schEditNumOfNodes = len(nodes)
                for i in range(self.schEditNumOfNodes):
                        # create new global labels from pin nodes
                        schEditNode = _KiSchEditNode()
                        schEditNode.parse(self.uuid, self.pos, nodes[i], i, pin.type)
                        self.schEditNodes.append(schEditNode)
                self.idx = idx

        def prepareForLayout(self, maxNodeNameLenInModule):
                # height of the connector
                # see text art at KiConst.schEdit
                # leftConn, rightConn
                self.height = KiConst.globalLabel["height"] * self.schEditNumOfNodes
                self.width = KiConst.globalLabel["leftToTextWidth"] + \
                             (maxNodeNameLenInModule * KiConst.globalLabel["charWidth"]) + \
                             KiConst.globalLabel["rightToTextWidth"]
                # iterate over each global label
                # offset them inside the connector
                for i in range(self.schEditNumOfNodes):
                        self.schEditNodes[i].prepareForLayout(self.width)
                # offset of the connector container based on order in leftConn/rightConn
                self.y = KiConst.schEdit["connyGap"] * self.idx

        def autoLayout(self, x, y):
                # offset to the page in schematic editor
                self.x = self.x + x
                self.y = self.y + y
                # offset each global label to the page in schematic editor
                for i in range(self.schEditNumOfNodes):
                        self.schEditNodes[i].autoLayout(self.x, self.y)

# data structure for a wire
class _KiSchEditWire:
        def __init__(self, parentUuid, idx, name):
                # start point x
                self.x0 = 0
                # end point x
                self.x1 = 0
                # start point y
                self.y0 = 0
                # end point y
                self.y1 = 0
                # length of the wire
                self.len = 0
                # orientation
                self.o = '' # v(vertical) or h(horizontal)
                self.name = name
                self.idx = idx
                self.uuid = KiUtil.getUuid("_KiSchEditWire" +
                                           parentUuid +
                                           self.name +
                                           str(self.idx))

        # it takes below parameters below and calculates end points
        # params:
        # x     : starting point in x axis
        # y     : starting point in y axis
        # o     : orientation
        # len   : length of the wire
        def prepareForLayout(self, x, y, o, len):
                self.x0 = x
                self.y0 = y
                self.o = o
                self.len = len
                if self.o == 'v':
                        self.x1 = self.x0
                        self.y1 = self.y0 + self.len
                elif self.o == 'h':
                        self.x1 = self.x0 + self.len
                        self.y1 = self.y0
                else:
                        raise Exception("ERROR undefined wire(" + self.name + ") orientation.")

        # offset the wire to page
        def autoLayout(self, x, y):
                self.x0 = self.x0 + x
                self.y0 = self.y0 + y
                self.x1 = self.x1 + x
                self.y1 = self.y1 + y

        # I know what I am doing mode
        # it also allows to draw wires in arbitrary angles
        def custom(self, x0, y0, x1, y1):
                self.x0 = x0
                self.y0 = y0
                self.x1 = x1
                self.y1 = y1

# Wire container container
# see KiConst.schEdit text art
# leftWire/rightWire
class _KiSchEditWireCont:
        def __init__(self):
                self.width = 0
                self.schEditConns = None # _KiSchEditConn
                self.numOfSchEditConns = 0
                self.wires = [] # _KiSchEditWire
                self.pos = ""
                self.x = 0
                self.y = 0
                self.endPoints = [
                # {
                # "uuid"
                # "x"
                # "y"
                # }
                ]
                self.numOfEndPoints = 0
                # connector with multiple global labels exist
                self.connWMultipleNodesExist = False
                self.uuid = ""

        def parse(self, parentUuid, schEditConns):
                self.schEditConns = schEditConns
                self.numOfSchEditConns = len(self.schEditConns)
                # so all of nodes in connector should have same pos
                # so just looking at first one
                self.pos = self.schEditConns[0].pos
                for i in range(self.numOfSchEditConns):
                        if self.schEditConns[i].schEditNumOfNodes > 1:
                                self.connWMultipleNodesExist = True
                                break
                self.uuid = KiUtil.getUuid("_KiSchEditWireCont" +
                                            parentUuid +
                                            self.pos)

        # offseting inside of a connector
        # leftWire/rightWire
        # connect labels to each other
        def __prepareLeftWireMultiNode(self, schEditConn, totalNode):
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
                        wire = _KiSchEditWire(self.uuid, j, "NodeToConnVerticalWire_" + schEditNode.name)
                        x = 0
                        y = (schEditConn.idx * KiConst.schEdit["connyGap"]) + \
                        (KiConst.globalLabel["height"] * (schEditNode.idx + totalNode)) + \
                        (KiConst.globalLabel["height"] / 2)
                        wire.prepareForLayout(x, y, 'h', KiConst.schEdit["wirexGap"])
                        self.wires.append(wire)
                # End NodeToConnVerticalWire

                # Begin ConnVerticalWire
                wire = _KiSchEditWire(self.uuid, 0, "ConnVerticalWire_"+schEditConn.name)
                x = KiConst.schEdit["wirexGap"]
                y = (schEditConn.idx * KiConst.schEdit["connyGap"]) + \
                (KiConst.globalLabel["height"] * (schEditConn.schEditNodes[0].idx + totalNode)) + \
                (KiConst.globalLabel["height"] / 2)
                len = (schEditConn.schEditNumOfNodes - 1) * KiConst.globalLabel["height"]
                wire.prepareForLayout(x, y, 'v', len)
                self.wires.append(wire)
                # End ConnVerticalWire

                wire = _KiSchEditWire(self.uuid, 0, "__prepareLeftWireMultiNode_Endpoint_"+schEditConn.name)
                y = y + len/2
                len = KiConst.schEdit["wirexGap"]
                wire.prepareForLayout(x, y, 'h', len)
                self.wires.append(wire)

                endPoint = {
                        "uuid" : schEditConn.uuid,
                        "x" : x + len,
                        "y" : y
                }
                self.endPoints.append(endPoint)

        # just draw a wire at the tip of global label
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

                wire = _KiSchEditWire(self.uuid, 0, "__prepareWireSingleNode_Endpoint_" + schEditNode.name)
                wire.prepareForLayout(x, y, 'h', len)
                self.wires.append(wire)

                if self.pos == "left":
                        x = x + len

                endPoint = {
                        "uuid" : schEditConn.uuid,
                        "x" : x,
                        "y" : y
                }
                self.endPoints.append(endPoint)

        # just another wrapper for offseting multi node and single node connectors
        def __prepareWireContainer(self):
                # total number of nodes
                # used for offseting
                totalNode = 0
                for i in range(self.numOfSchEditConns):
                        schEditConn = self.schEditConns[i]
                        # the way we draw wires for connector with multiple global labels is:
                        # first connect global labels with each other
                        multiNode = schEditConn.schEditNumOfNodes > 1
                        if multiNode and self.pos == "right":
                                raise Exception("ERROR right conn container can NOT have multiple nodes.\n"
                                                "Not supported. Could u implement please?")
                        elif schEditConn.schEditNumOfNodes > 1:
                                self.__prepareLeftWireMultiNode(schEditConn, totalNode)
                        else:
                                self.__prepareWireSingleNode(schEditConn, totalNode)
                        totalNode = totalNode + schEditConn.schEditNumOfNodes
                self.numOfEndPoints = len(self.endPoints)


        def prepareForLayout(self):
                # just giving more space if multinode exist
                # so wires are not close to each other
                if self.connWMultipleNodesExist:
                        self.width = KiConst.schEdit["wirexGap"] * 6
                else:
                        self.width = KiConst.schEdit["wirexGap"] * 4
                self.__prepareWireContainer()

        # offseting to page
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
                self.uuid = ""

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
                self.uuid = symEditSym.sym.uuid
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
                for pos in KiConst.availPinPoss:
                        self.numOfSchEditConns[pos] = len(self.schEditConns[pos])
                
                for pos in KiConst.availPinPoss:
                        if self.numOfSchEditConns[pos] != 0:
                                self.schEditWireCont[pos] = _KiSchEditWireCont()
                                self.schEditWireCont[pos].parse(self.uuid, self.schEditConns[pos])

        def __getMaxNodeNameLen(self):
                maxNodeNameLen = {
                        "left" : 0,
                        "right" : 0
                }
                for pos in KiConst.availPinPoss:
                        for i in range(self.numOfSchEditConns[pos]):
                                for j in range(self.schEditConns[pos][i].schEditNumOfNodes):
                                        nodeName = self.schEditConns[pos][i].schEditNodes[j].name
                                        if len(nodeName) > maxNodeNameLen[pos]:
                                                maxNodeNameLen[pos] = len(nodeName)
                return maxNodeNameLen
        
        def __calculateWidth(self):
                for pos in KiConst.availPinPoss:
                        maxWidth = 0
                        for i in range(self.numOfSchEditConns[pos]):
                                if self.schEditConns[pos][i].width > maxWidth:
                                        maxWidth = self.schEditConns[pos][i].width
                        self.width = self.width + maxWidth


                for pos in KiConst.availPinPoss:
                        if self.numOfSchEditConns[pos] != 0:
                                self.schEditWireCont[pos].prepareForLayout()
                                self.width = self.width + self.schEditWireCont[pos].width
                                
                self.width = self.width + self.symEditSym.width

        def __calculateHeight(self):
                for pos in KiConst.availPinPoss:
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

        def prepareForLayout(self):
                maxNodeNameLen = self.__getMaxNodeNameLen()

                for pos in KiConst.availPinPoss:
                        for i in range(self.numOfSchEditConns[pos]):
                                self.schEditConns[pos][i].prepareForLayout(maxNodeNameLen[pos])

                self.__calculateWidth()
                self.__calculateHeight()

        # laying final wires
        def __connectConnToSymbol(self):
                for pos in KiConst.availPinPoss:
                        # do nothing if there is no connector
                        if self.numOfSchEditConns[pos] == 0:
                                continue

                        for i in range(self.symEditSym.sym.numOfPins):
                                symEditPin = self.symEditSym.symEditPins[i]
                                for j in range(self.schEditWireCont[pos].numOfEndPoints):
                                        endPoint = self.schEditWireCont[pos].endPoints[j]
                                        # nothing to connect if their names dont match
                                        if endPoint["uuid"] != symEditPin.pin.conn.uuid:
                                                continue
                                        wire = _KiSchEditWire(endPoint["uuid"], j, "Final_" + symEditPin.pin.conn.name)
                                        wire.custom(endPoint["x"],
                                                endPoint["y"],
                                                symEditPin.x + self.symx,
                                                abs(symEditPin.y) + self.symy)
                                        self.finalWires.append(wire)
                self.numOfFinalWires = len(self.finalWires)

        def __findStartConnyOffset(self, pos):
                connyOffset = 0
                if self.height > self.schEditConnsHeight[pos]:
                        connyOffset = (self.height - self.schEditConnsHeight[pos]) / 2
                        # round it so every connector get located in grid point
                        connyOffset = KiUtil.roundToGrid(connyOffset)
                return connyOffset

        # this is tricky
        def autoLayout(self, x, y):
                # centering in y axis
                leftConnyOffset = self.__findStartConnyOffset("left")

                for i in range(self.numOfSchEditConns["left"]):
                        self.schEditConns["left"][i].autoLayout(x, y + leftConnyOffset)
                        leftConnyOffset = leftConnyOffset + self.schEditConns["left"][i].height

                if self.numOfSchEditConns["left"] != 0:
                        endOfLeftConnx = self.schEditConns["left"][0].x + self.schEditConns["left"][0].width
                        startOfLeftConny = self.schEditConns["left"][0].y
                        self.schEditWireCont["left"].autoLayout(endOfLeftConnx, startOfLeftConny)

                # begin of offseting symbol in page
                # if there is left connectors there is also wires
                if self.numOfSchEditConns["left"] != 0:
                        endOfLeftWireContx = self.schEditWireCont["left"].x + self.schEditWireCont["left"].width
                        self.symx = endOfLeftWireContx
                else:
                        self.symx = x
                # centering in y axis
                self.symy = y + (self.height-self.symEditSym.height) / 2 - KiConst.symEdit["charHeight"]
                # rounding to grid so pins are user clickable
                self.symx = KiUtil.roundToGrid(self.symx)
                self.symy = KiUtil.roundToGrid(self.symy)

                self.desigx = self.symx + KiConst.schEdit["desigxOffset"]
                self.desigy = self.symy + KiConst.schEdit["desigyOffset"]
                # end of offseting symbol in page

                # centering in y axis
                rightConnyOffset = self.__findStartConnyOffset("right")

                # if there is right connectors there is also wires
                if self.numOfSchEditConns["right"] != 0:
                        endOfSymx = self.symx + self.symEditSym.width
                        self.schEditWireCont["right"].autoLayout(endOfSymx, y + rightConnyOffset)

                for i in range(self.numOfSchEditConns["right"]):
                        # there needs to be wire container if any container exist
                        endOfWireContx = self.schEditWireCont["right"].x + self.schEditWireCont["right"].width
                        self.schEditConns["right"][i].autoLayout(endOfWireContx, y + rightConnyOffset)
                        rightConnyOffset = rightConnyOffset + self.schEditConns["right"][i].height

                self.__connectConnToSymbol()


class KiSchEditPrj:
        def __init__(self, logFolderPath, showPinNumbers):
                self.schEditModules = [] # _KiSchEditModule
                self.projectName = ""
                self.numOfSchEditModules = 0
                self.symEditLibs = [] # KiSymEditLib
                self.pageWidth = 0
                self.pageHeight = 0
                self.logFolderPath = logFolderPath
                self.showPinNumbers = showPinNumbers
                self.uuid = ""

        def __createSchEditModules(self):
                for i in range(len(self.symEditLibs)):
                        for j in range(self.symEditLibs[i].lib.numOfSymbols):
                                symEditSym = self.symEditLibs[i].getSymEditSymFromDesig(self.symEditLibs[i].lib.symbols[j].name,
                                                                                        self.symEditLibs[i].lib.symbols[j].designator)
                                schEditModule = _KiSchEditModule()
                                schEditModule.parse(self.symEditLibs[i].lib.name, symEditSym)
                                self.schEditModules.append(schEditModule)
                self.numOfSchEditModules = len(self.schEditModules)

        def parse(self, prj, symEditLibs, pageWidth, pageHeight):
                self.symEditLibs = symEditLibs
                self.projectName = prj.name
                self.uuid = prj.uuid
                self.pageHeight = pageHeight
                self.pageWidth = pageWidth

                self.__createSchEditModules()
                # offseting inside of their own containers
                for i in range(self.numOfSchEditModules):
                        self.schEditModules[i].prepareForLayout()
                # begin module page layout
                modulexOffset = 0
                moduleyOffset = 0
                # max width in vertically layout symbols
                maxWidth = 0
                for i in range(self.numOfSchEditModules):
                        # does it fit into page
                        if moduleyOffset + self.schEditModules[i].height < self.pageHeight:
                                self.schEditModules[i].autoLayout(modulexOffset, moduleyOffset)
                                if self.schEditModules[i].width > maxWidth:
                                        maxWidth = self.schEditModules[i].width
                        else: # it did not fit into page
                                # start from last vertically layout symbols end
                                modulexOffset = modulexOffset + maxWidth + KiConst.schEdit["modulexGap"]
                                # start from top of the page again
                                moduleyOffset = 0
                                # since this is the first module in vertical layout. maxWidth equals to its own
                                maxWidth = self.schEditModules[i].width
                                self.schEditModules[i].autoLayout(modulexOffset, moduleyOffset)
                        # mark of end layout out module
                        moduleyOffset = moduleyOffset + self.schEditModules[i].height + KiConst.schEdit["moduleyGap"]
                # end module page layout

                # did it fit into page
                if modulexOffset + maxWidth > self.pageWidth:
                        return False
                return True

        def __validateUuids(renderedText):
                lines = renderedText.split("\n")
                uuids = []

                for line in lines:
                        if not "uuid" in line:
                                continue
                        u = line.split("\"")[1]
                        uuids.append(u)

                uniqUuids = set(uuids)
                if len(uuids) != len(uniqUuids):
                        for u in uniqUuids:
                                uuids.remove(u)
                        raise Exception("Uuid is not unique->" + str(uuids))

        def gen(self, templateFilePath, outFolderPath):
                # basic jinja environment setup
                templateFileName = os.path.basename(templateFilePath)
                templateLoader = jinja2.FileSystemLoader(searchpath=os.path.dirname(templateFilePath))
                templateEnv = jinja2.Environment(loader=templateLoader)
                template = templateEnv.get_template(templateFileName)

                # change the filename to library name
                self.outFileName = templateFileName.replace(KiConst.invertedUniqDict["xproject.name"], self.projectName)

                outFilePath = os.path.join(outFolderPath, self.outFileName)
                renderedText = template.render(uuid=self.uuid,
                                               symEditLibs=self.symEditLibs,
                                               schEditModules = self.schEditModules,
                                               pageWidth=self.pageWidth,
                                               pageHeight=self.pageHeight,
                                               showPinNumbers=self.showPinNumbers,
                                               loggingEnabled=False)
                renderedText = KiUtil.removeEmptyLines(renderedText)
                KiSchEditPrj.__validateUuids(renderedText)
                with open(outFilePath, 'w') as f:
                        f.write(renderedText)

                # re rendering again with logging enabled and writing log folder
                outFolderPath = os.path.join(self.logFolderPath, self.projectName)
                if not os.path.exists(outFolderPath):
                        os.makedirs(outFolderPath)
                outLogFilePath = os.path.join(outFolderPath, "KiSchEdit_" + self.outFileName)
                renderedText = template.render(uuid=self.uuid,
                                               symEditLibs=self.symEditLibs,
                                               schEditModules = self.schEditModules,
                                               pageWidth=self.pageWidth,
                                               pageHeight=self.pageHeight,
                                               loggingEnabled=True,
                                               showPinNumbers=self.showPinNumbers)
                renderedText = KiUtil.removeEmptyLines(renderedText)
                with open(outLogFilePath, 'w') as f:
                        f.write(renderedText)
                return [outFilePath]
