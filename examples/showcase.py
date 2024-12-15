import os
import sys
from kiapi import KiApiItem, KiApi, KiApiItemCont

g_lib  ="MyLib"
g_symDesigs = ["MyIC1", "MyIC2", "MyIC3"]
g_csvStr = ""

def createItem(symIdx, style, type, pos, pinNum):
        item = KiApiItem()
        item.lib = g_lib
        item.sym = "MyIC"
        item.desig = g_symDesigs[symIdx]
        item.pin = type + "_" + style
        item.pinNumber = str(pinNum)
        item.pinPos = pos
        item.pinType = type
        item.pinStyle = style
        if pos == "left":
                for i in range(symIdx):
                        item.addGlobalLabel(item.pin + str(i))
        elif (symIdx % 2) == 0:
                item.addGlobalLabel(item.pin)

        return item

g_numSyms = len(g_symDesigs)

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

g_kiApi = KiApi(
        apiItemCont=g_apiItemCont,
        logFolderPath="log",
        outFolderPath="out/showcase",
        showPinNumbers=False
)

genPaths = g_kiApi.genPrj(216,384)

# print generated files
for g in genPaths:
        print("Gen: " + str(g))