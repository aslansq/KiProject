import os
import sys

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
        numOfAvailPinStyles = KiConst.numOfAvailPinStyles
        numOfAvailPinTypes  = KiConst.numOfAvailPinTypes
        numOfAvailPinPoss   = KiConst.numOfAvailPinPoss

        availPinStyles = KiConst.availPinStyles
        availPinTypes  = KiConst.availPinTypes
        availPinPoss   = KiConst.availPinPoss

        def getHeader():
                return "#Library,Symbol,SymbolDesignator,PinName,PinNumber,PinPos,PinType,PinStyle,Nodes"

        def __init__(self):
                self.lib       = "" # library name
                self.sym       = "" # symbol name
                self.desig     = "" # designator name
                self.pin       = "" # pin name
                self.pinNumber = ""
                self.pinPos    = "" # KiConst.availPinPoss
                self.pinType   = "" # KiConst.availPinTypes
                self.pinStyle  = "" # KiConst.availPinStyles
                self.nodes     = [] # just list of strings

        def toStr(self):
                s = self.lib       + "," + \
                    self.sym       + "," + \
                    self.desig     + "," + \
                    self.pin       + "," + \
                    self.pinNumber + "," + \
                    self.pinPos    + "," + \
                    self.pinType   + "," + \
                    self.pinStyle  + ","
                numOfNodes = len(self.nodes)
                for i in range(numOfNodes):
                    s = s + self.nodes[i]
                    if i != (numOfNodes-1):
                            s = s + "-"
                return s

class KiApi:
        def __init__(self,
                    csvFilePath=None, #  kiApiItems and csvFilePath is mutually exclusive.
                    kiApiItems=None,  #  only one is mandatory
                    kiApiItemsName=None, # if kiApiItems given mandatory
                    logFolderPath=None, # mandatory
                    outFolderPath=None, # mandatory
                    kicadVersion=g_latestKicadVersion, # optional, if not given: latest supported used
                    showPinNumbers=False): # optional
                self.__csvFilePath = None
                self.__csvStr = None
                self.__logFolderPath = None
                self.__outFolderPath = None
                self.__kicadVersion = kicadVersion
                self.showPinNumbers = showPinNumbers
                # start filled by __setTemplateDirPath
                self.__equivalentKicadVersion = ""
                self.__templateDirPath = None
                # end filled by __setTemplateDirPath
                # start filled by __parse
                self.__prj = None
                # end filled by __parse

                self.__validity(csvFilePath,
                                kiApiItems,
                                kiApiItemsName,
                                logFolderPath,
                                outFolderPath)

                if kiApiItems != None:
                        self.__createCsvStrFromItems(kiApiItems)
                        self.__kiApiItemsName = kiApiItemsName
                else:
                        self.__csvFilePath = csvFilePath

                self.__logFolderPath = logFolderPath
                self.__outFolderPath = outFolderPath

                self.__setTemplateDirPath()
                self.__parse()

        def __validity(self,
                       csvFilePath,
                       kiApiItems,
                       kiApiItemsName,
                       logFolderPath,
                       outFolderPath):
                if kiApiItems != None and csvFilePath != None:
                        raise Exception("ERR KiApi dual input")

                if csvFilePath == None and kiApiItems == None:
                        raise Exception("ERR no input is given to KiApi")

                if kiApiItems == None and not os.path.exists(csvFilePath):
                        raise Exception("ERR csv file(" + str(self.__csvFilePath) + ") not exists.")

                if kiApiItems != None and kiApiItemsName == None:
                        raise Exception("ERR KiApi items name has not given")

                if logFolderPath == None:
                        raise Exception("ERR no log folder is given to KiApi")
                
                if outFolderPath == None:
                        raise Exception("ERR no out folder is given to KiApi")

                if not os.path.exists(logFolderPath):
                        raise Exception("ERR log folder(" + str(self.__logFolderPath) + ") not exist.")

                if not os.path.exists(outFolderPath):
                        raise Exception("ERR out folder(" + str(self.__outFolderPath) + ") not exists.")

        def __createCsvStrFromItems(self, kiApiItems):
                numOfItems = len(kiApiItems)
                self.__csvStr = KiApiItem.getHeader() + "\n"
                for i in range(numOfItems):
                        self.__csvStr = self.__csvStr + kiApiItems[i].toStr() + "\n"

        def genLib(self):
                symEditLibs = []
                for i in range(self.__prj.numOfLibs):
                        symEditLib = KiSymEditLib(self.__logFolderPath, self.showPinNumbers)
                        symEditLib.parse(self.__prj.name, self.__prj.libs[i])
                        symEditLibs.append(symEditLib)

                for i in range(len(symEditLibs)):
                        absPath = os.path.join(self.__templateDirPath, "e5ea7ba.kicad_sym")
                        symEditLibs[i].gen(absPath, self.__outFolderPath)

                return symEditLibs
        
        def genPrj(self, pageHeight, pageWidth):
                symEditLibs = self.genLib()

                absPath = os.path.join(self.__templateDirPath, "f135d3a.kicad_sch")
                schEditPrj = KiSchEditPrj(self.__logFolderPath, self.showPinNumbers)
                retVal = schEditPrj.parse(self.__prj.name, symEditLibs, pageWidth, pageHeight)
                if retVal == False:
                        print("WARN: Project(" + self.__prj.name + ") did not fit into page.")
                schEditPrj.gen(absPath, self.__outFolderPath)

                absPath = os.path.join(self.__templateDirPath, "f135d3a.kicad_pro")
                pro = KiPro(self.__prj.name)
                pro.gen(absPath, self.__outFolderPath)

                absPath = os.path.join(self.__templateDirPath, "f135d3a.kicad_prl")
                pro = KiPrl(self.__prj.name)
                pro.gen(absPath, self.__outFolderPath)

                absPath = os.path.join(self.__outFolderPath, self.__prj.name + ".kicad_pcb")
                KiUtil.copyPaste(os.path.join(self.__templateDirPath, "f135d3a.kicad_pcb"),
                                absPath)
                print("Copy To: " + str(absPath))

                absPath = os.path.join(self.__templateDirPath, "sym-lib-table")
                g_pro = KiSymLibTable(self.__prj)
                g_pro.gen(absPath, self.__outFolderPath)

        def __parse(self):
                self.__prj = KiPrj(self.__logFolderPath)
                if self.__csvStr != None:
                        self.__prj.parseFromStr(self.__kiApiItemsName, self.__csvStr)
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