import os
import sys
import copy

g_homePath = None
try:
        g_homePath = os.environ['KI_PROJECT_HOME']
        scriptsPath = os.path.join(g_homePath, "scripts")
        sys.path.append(scriptsPath)
except Exception as e:
        raise Exception("KI_PROJECT_HOME environment variable is not found")

from kiprj import KiPrj
from kisymedit import KiSymEditLib
from kischedit import KiSchEditPrj
from kipro import KiPro
from kiutil import KiUtil
from kisymlibtable import KiSymLibTable
from kiprl import KiPrl
from kiconst import KiConst

g_latestKicadVersion = "v8"

class KiApiItem:
        def __init__(self):
                self.lib       = "" # library name
                self.sym       = "" # symbol name
                self.desig     = "" # designator name
                self.pin       = "" # pin name
                self.pinNumber = ""
                self.pinPos    = "" # KiConst.availPinPoss
                self.pinType   = "" # KiConst.availPinTypes
                self.pinStyle  = "" # KiConst.availPinStyles
                self.__nodes     = [] # just list of strings

        def addGlobalLabel(self, name):
                if type(name) != str:
                        raise Exception("Global label name should be string")
                self.__nodes.append(name)

        def _toStr(self):
                s = self.lib       + "," + \
                    self.sym       + "," + \
                    self.desig     + "," + \
                    self.pin       + "," + \
                    self.pinNumber + "," + \
                    self.pinPos    + "," + \
                    self.pinType   + "," + \
                    self.pinStyle  + ","
                numOfNodes = len(self.__nodes)
                for i in range(numOfNodes):
                    s = s + self.__nodes[i]
                    if i != (numOfNodes-1):
                            s = s + "-"
                return s

        def _validity(self, apiContName):
                init = apiContName + "->KiApiItem invalid config:\n"

                s = init

                if self.lib == "":
                        s = s + "lib\n"
                if self.sym == "":
                        s = s + "sym\n"
                if self.desig == "":
                        s = s + "desig\n"
                if self.pin == "":
                        s = s + "pin\n"
                if self.pinNumber == "":
                        s = s + "pinNumber\n"

                if not self.pinPos in KiConst.availPinPoss:
                        s = s + "pinPos(" + self.pinPos + ")\n"
                if not self.pinType in KiConst.availPinTypes:
                        s = s + "pinType(" + self.pinType + ")\n"
                if not self.pinStyle in KiConst.availPinStyles:
                        s = s + "pinStyle(" + self.pinStyle + ")\n"

                if s != init:
                        raise Exception(s)

class KiApiItemCont:
        numOfAvailPinStyles = KiConst.numOfAvailPinStyles
        numOfAvailPinTypes  = KiConst.numOfAvailPinTypes
        numOfAvailPinPoss   = KiConst.numOfAvailPinPoss

        availPinStyles = KiConst.availPinStyles
        availPinTypes  = KiConst.availPinTypes
        availPinPoss   = KiConst.availPinPoss

        def __init__(self):
                self.name = None
                self.__apiItems = []

        def add(self, apiItem):
                if type(apiItem) != KiApiItem:
                        raise Exception("apiItem should have KiApiItem type")
                self.__apiItems.append(copy.copy(apiItem))

        def _validity(self):
                if self.name == None:
                        raise Exception("KiApiCont is not valid")
                for i in range(len(self.__apiItems)):
                        self.__apiItems[i]._validity(self.name)

        def _getCsvStr(self):
                numOfApiItems = len(self.__apiItems)
                csvStr = KiApiItemCont._getHeader() + "\n"
                for i in range(numOfApiItems):
                        csvStr = csvStr + self.__apiItems[i]._toStr() + "\n"
                return csvStr

        def _getHeader():
                return "#Library,Symbol,SymbolDesignator,PinName,PinNumber,PinPos,PinType,PinStyle,GlobalLabels"

class KiApi:
        def __init__(self,
                    csvFilePath=None, #  apiItemCont and csvFilePath is mutually exclusive.
                    apiItemCont=None,
                    logFolderPath=None, # mandatory
                    outFolderPath=None, # mandatory
                    showPinNumbers=False): # optional
                self.__csvFilePath = None
                self.__apiItemCont = None
                self.__logFolderPath = None
                self.__outFolderPath = None
                # for now there is only one kicad version supported
                # maybe in the future, we will get as argument
                self.__kicadVersion = g_latestKicadVersion
                self.__showPinNumbers = showPinNumbers
                # start filled by __setTemplateDirPath
                self.__equivalentKicadVersion = ""
                self.__templateDirPath = None
                # end filled by __setTemplateDirPath
                # start filled by __parse
                self.__prj = None
                # end filled by __parse

                self.__validity(csvFilePath,
                                apiItemCont,
                                logFolderPath,
                                outFolderPath)
                
                logFolderPath = os.path.abspath(logFolderPath)
                outFolderPath = os.path.abspath(outFolderPath)

                if apiItemCont != None:
                        self.__apiItemCont = apiItemCont
                else:
                        self.__csvFilePath = csvFilePath

                self.__logFolderPath = logFolderPath
                self.__outFolderPath = outFolderPath

                self.__setTemplateDirPath()
                self.__parse()

        def __validity(self,
                       csvFilePath,
                       apiItemCont,
                       logFolderPath,
                       outFolderPath):
                if apiItemCont != None and csvFilePath != None:
                        raise Exception("ERR KiApi dual input")

                if csvFilePath == None and apiItemCont == None:
                        raise Exception("ERR no input is given to KiApi")

                if apiItemCont == None and not os.path.exists(csvFilePath):
                        raise Exception("ERR csv file(" + str(csvFilePath) + ") not exists.")

                if apiItemCont != None:
                        apiItemCont._validity()

                if logFolderPath == None:
                        raise Exception("ERR no log folder is given to KiApi")
                
                if outFolderPath == None:
                        raise Exception("ERR no out folder is given to KiApi")

                if not os.path.exists(logFolderPath):
                        raise Exception("ERR log folder(" + str(logFolderPath) + ") not exist.")

                if not os.path.exists(outFolderPath):
                        raise Exception("ERR out folder(" + str(outFolderPath) + ") not exists.")

        def __genLib(self):
                symEditLibs = []
                genPaths = []
                for i in range(self.__prj.numOfLibs):
                        symEditLib = KiSymEditLib(self.__logFolderPath, self.__showPinNumbers)
                        symEditLib.parse(self.__prj.name, self.__prj.libs[i])
                        symEditLibs.append(symEditLib)

                for i in range(len(symEditLibs)):
                        absPath = os.path.join(self.__templateDirPath, "e5ea7ba.kicad_sym")
                        g = symEditLibs[i].gen(absPath, self.__outFolderPath)
                        genPaths = genPaths + g

                return symEditLibs, genPaths
        
        def genLib(self):
                symEditLibs, genPaths = self.__genLib()
                return genPaths

        def genPrj(self, pageHeight, pageWidth):
                symEditLibs, genPaths = self.__genLib()

                absPath = os.path.join(self.__templateDirPath, "f135d3a.kicad_sch")
                schEditPrj = KiSchEditPrj(self.__logFolderPath, self.__showPinNumbers)
                schEditPrj.parse(self.__prj, symEditLibs, pageWidth, pageHeight)
                g = schEditPrj.gen(absPath, self.__outFolderPath)
                genPaths = genPaths + g

                absPath = os.path.join(self.__templateDirPath, "f135d3a.kicad_pro")
                pro = KiPro(self.__prj.name)
                g = pro.gen(absPath, self.__outFolderPath)
                genPaths = genPaths + g

                absPath = os.path.join(self.__templateDirPath, "f135d3a.kicad_prl")
                pro = KiPrl(self.__prj.name)
                g = pro.gen(absPath, self.__outFolderPath)
                genPaths = genPaths + g

                absPath = os.path.join(self.__outFolderPath, self.__prj.name + ".kicad_pcb")
                KiUtil.copyPaste(os.path.join(self.__templateDirPath, "f135d3a.kicad_pcb"),
                                absPath)
                genPaths.append(absPath)

                absPath = os.path.join(self.__templateDirPath, "sym-lib-table")
                g_pro = KiSymLibTable(self.__prj)
                g = g_pro.gen(absPath, self.__outFolderPath)
                genPaths = genPaths + g
                return genPaths

        def __parse(self):
                self.__prj = KiPrj(self.__logFolderPath)
                if self.__apiItemCont != None:
                        self.__prj.parseFromStr(self.__apiItemCont.name, self.__apiItemCont._getCsvStr())
                if self.__csvFilePath != None:
                        self.__prj.parse(self.__csvFilePath)
                self.__prj.log()

        def __setTemplateDirPath(self):
                self.__equivalentKicadVersion = self.__getEquivalentKicadVersion(self.__kicadVersion)
                if self.__equivalentKicadVersion == "":
                       s = "ERR can not find equivalent version in lookup table"
                       s = s + "ERR Kicad version->" + self.__kicadVersion
                       raise Exception(s)
                else:
                        absPath = os.path.join(g_homePath, "templates/" + self.__equivalentKicadVersion)
                        if not os.path.exists(absPath):
                                s = "templates does not exist for that version requested " \
                                    + self.__kicadVersion + " equivalent " + self.__equivalentKicadVersion + "\n"
                                s = s + "looked for templates here->" + str(absPath)
                                raise Exception(s)
                        self.__templateDirPath = absPath

        def __getEquivalentKicadVersion(self, kicadVersion):
                equivalentVersion = ""
                lookupTablePath = os.path.join(g_homePath, "templates/version_lookup_table.csv")
                try: # file open operation and out of bound in items
                        file = open(lookupTablePath)
                        for line in file:
                                items = line.split(',')
                                if items[0][0] == "#":
                                        continue
                                if len(items) != 2:
                                        s = str(lookupTablePath) + "\n"
                                        s = s + "number of items in a given line should be 2 " + line
                                        raise Exception(s)
                                if items[0] == kicadVersion:
                                        equivalentVersion = items[1]
                                        break
                        file.close()
                except Exception as e:
                        s = str(lookupTablePath) + "\n"
                        s = s + str(e)
                        raise Exception(s)
                return equivalentVersion