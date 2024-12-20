from kiapi import KiApiItem, KiApi, KiApiItemCont

apiItemCont = KiApiItemCont()
apiItemCont.name = "SimpleProject"

apiItem = KiApiItem()
apiItem.lib = "SimpleLib"
apiItem.sym = "SimpleSym1"
apiItem.desig = "SimpleDesig1"
apiItem.pin = "Pin1"
apiItem.pinNumber = "1"
apiItem.pinPos = "left"
apiItem.pinType = "bidirectional"
apiItem.pinStyle = "line"

apiItemCont.add(apiItem)

g_kiApi = KiApi(
        apiItemCont=apiItemCont,
        logFolderPath="log",
        outFolderPath="out/simple",
        showPinNumbers=False
)

genPaths = g_kiApi.genPrj(216,384)

# print generated files
for g in genPaths:
        print("Gen: " + str(g))
