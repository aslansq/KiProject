import os
import sys

import os
try:
        home = os.environ['KI_PROJECT_HOME']
        sys.path.append(home)
except Exception as e:
        raise Exception("KI_PROJECT_HOME environment variable is not found")

from kiapi import KiApiItem, KiApi, KiApiItemCont

apiItemCont = KiApiItemCont()
apiItemCont.name = "SimpleProject"

# begin of symbol 1
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

apiItem.pin = "Pin2"
apiItem.pinNumber = "2"
apiItemCont.add(apiItem)

apiItem.pin = "Pin3"
apiItem.pinNumber = "3"
apiItem.pinPos = "right"
apiItemCont.add(apiItem)

apiItem.pin = "Pin4"
apiItem.pinNumber = "4"
apiItemCont.add(apiItem)
# end of symbol 1

# begin of symbol 2
apiItem.sym = "SimpleSym2"
apiItem.desig = "SimpleDesig2"
apiItem.pin = "Pin1"
apiItem.pinNumber = "1"
apiItem.pinPos = "left"

apiItemCont.add(apiItem)

apiItem.pin = "Pin2"
apiItem.pinNumber = "2"
apiItemCont.add(apiItem)

apiItem.pin = "Pin3"
apiItem.pinNumber = "3"
apiItem.pinPos = "right"
apiItemCont.add(apiItem)

apiItem.pin = "Pin4"
apiItem.pinNumber = "4"
apiItemCont.add(apiItem)
# end of symbol 2

outPath = os.path.abspath("out")
prjPath = os.path.join(outPath, "simple")
logFolderPath = os.path.abspath("log")

g_kiApi = KiApi(
        apiItemCont=apiItemCont,
        logFolderPath=logFolderPath,
        outFolderPath=prjPath,
        showPinNumbers=False
)

g_kiApi.genPrj(216,384)
