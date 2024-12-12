import os
import sys

import os
try:
        home = os.environ['KI_PROJECT_HOME']
        sys.path.append(home)
except Exception as e:
        raise Exception("KI_PROJECT_HOME environment variable is not found")

from kiapi import KiApiItem, KiApi

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

g_csvStr = KiApiItem.getHeader() + "\n"
g_items = []

for i in range(g_numSyms):
        g_pinNum = 0
        for j in range(KiApiItem.numOfAvailPinStyles):
                for k in range(KiApiItem.numOfAvailPinTypes):
                        for l in range(KiApiItem.numOfAvailPinPoss):
                                item = createItem(
                                        i,
                                        KiApiItem.availPinStyles[j],
                                        KiApiItem.availPinTypes[k],
                                        KiApiItem.availPinPoss[l],
                                        g_pinNum
                                )
                                g_items.append(item)
                                g_pinNum = g_pinNum + 1

g_outPath = os.path.abspath("out")
if not os.path.exists(g_outPath):
        os.makedirs(g_outPath)

g_prjPath = os.path.join(g_outPath, "showcase")
if not os.path.exists(g_prjPath):
        os.makedirs(g_prjPath)

g_logFolderPath = os.path.abspath("log")
if not os.path.exists(g_logFolderPath):
        os.makedirs(g_logFolderPath)

g_kiApi = KiApi(
        kiApiItems=g_items,
        kiApiItemsName="showcase",
        logFolderPath=g_logFolderPath,
        outFolderPath=g_prjPath,
        showPinNumbers=False
)

g_kiApi.genPrj(216,384)