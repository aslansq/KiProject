# this file is going to be used for autolayout schematic editor

from kiconst import KiConst
import jinja2
import os

class _KiSchEditNode:
        def __init__(self):
                self.node = ""
                self.x = 0
                self.y = 0
        
        def parse(self, node):
                self.node = node

class _KiSchEditConn:
        def __init__(self):
                self.x = 0
                self.y = 0
                self.schEditNodes = [] # class _KiSchEditNode type
                self.conn = None
        
        def parse(self, conn):
                self.conn = conn
                for i in range(self.conn.numOfNodes):
                        schEditNode = _KiSchEditNode()
                        schEditNode.parse(self.conn.nodes[i])
                        self.schEditNodes.append(schEditNode)

class _KiSchEditPin:
        def __init__(self):
                self.symEditPin = []
                self.schEditConn = _KiSchEditConn()
                self.x = 0
                self.y = 0
        
        def parse(self, symEditPin):
                self.symEditPin = symEditPin
                self.schEditConn.parse(symEditPin.pin.conn)

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

class KiSchEditPrj:
        def __init__(self):
                self.symEditLibs = None # KiSymEditLib type
                self.schEditSyms = []
                self.projectName = ""

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
