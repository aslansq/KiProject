import os
import sys

import os
try:
        home = os.environ['KI_PROJECT_HOME']
        sys.path.append(home)
except Exception as e:
        raise Exception("KI_PROJECT_HOME environment variable is not found")

from kiapi import KiApiItem, KiApi, KiApiItemCont

g_lib  ="MyLib"
g_syms = ["MyIC1", "MyIC2", "MyIC3"]
g_csvStr = ""

def createItem(symIdx, style, type, pos, pinNum):
        item = KiApiItem()
        item.lib = g_lib
        item.sym = g_syms[symIdx]
        item.desig = g_syms[symIdx]
        item.pin = type + "_" + style + "_" + str(pinNum)
        item.pinNumber = str(pinNum)
        item.pinPos = pos
        item.pinType = type
        item.pinStyle = style
        if pos == "left":
                for i in range(symIdx):
                        item.nodes.append(item.pin + "_" + str(i))
        elif (symIdx % 2) == 0:
                item.nodes.append(item.pin)

        return item

g_numSyms = len(g_syms)

g_apiItemCont = KiApiItemCont()
g_apiItemCont.name = "showcase"

for i in range(g_numSyms):
        g_pinNum = 0
        for j in range(KiApiItemCont.numOfAvailPinStyles):
                for k in range(KiApiItemCont.numOfAvailPinTypes):
                        for l in range(KiApiItemCont.numOfAvailPinPoss):
                                item = createItem(
                                        i,
                                        KiApiItemCont.availPinStyles[j],
                                        KiApiItemCont.availPinTypes[k],
                                        KiApiItemCont.availPinPoss[l],
                                        g_pinNum
                                )
                                g_apiItemCont.add(item)
                                g_pinNum = g_pinNum + 1

g_outPath = os.path.abspath("out")
g_prjPath = os.path.join(g_outPath, "showcase")
g_logFolderPath = os.path.abspath("log")

g_kiApi = KiApi(
        apiItemCont=g_apiItemCont,
        logFolderPath=g_logFolderPath,
        outFolderPath=g_prjPath,
        showPinNumbers=False
)

g_kiApi.genPrj(216,384)