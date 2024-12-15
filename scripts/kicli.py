import csv
import sys
import os
import getopt
try:
        home = os.environ['KI_PROJECT_HOME']
        sys.path.append(home)
except Exception as e:
        raise Exception("KI_PROJECT_HOME environment variable is not found")
from kiapi import KiApi
from kiapi import KiApiItemCont

g_args = {
    "csvFilePath" : None,
    "outFolderPath" : None,
    "logFolderPath" : None,
    "pageWidth" : 1366,
    "pageHeight": 768,
    "pinNumbers" : False,
    "justLib" : False
}
g_argList = sys.argv[1:]
g_opts = "hpjl:c:o:t:h:w:"
g_longOpts = ["help", "pinNumbers", "justLib", "logFolderPath=", "csvFilePath=", "outFolderPath=", "pageHeight=", "pageWidth="]
g_symEditLibs = []
g_prj = None

def getCsvFileExample():
        s = KiApiItemCont._getHeader()
        header = s.split(",")
        numOfCols = len(header)
        maxs = []
        for i in range(numOfCols):
                maxs.append(len(header[i]))

        s = "ATtiny1627,ATtiny3224,ATtiny3224,VDD,1,left,input,line,"
        example = s.split(",")
        for i in range(numOfCols):
                if len(example[i]) > maxs[i]:
                        maxs[i] = len(example[i])

        s = "Example command:\n"

        s = s + (
                "kicli \\\n"
                "--csvFilePath microchip.csv \\\n"
                "--outFolderPath microchip \\\n"
                "--logFolderPath log \\\n"
                "--pageWidth 384 \\\n"
                "--pageHeight 216 \\\n"
                "--pinNumbers\n"
        )
        s = s + "\n"

        s = s + "Content of microchip.csv:\n"
        for i in range(numOfCols):
                if i != 0:
                        s = s + ","
                s = s + header[i].ljust(maxs[i])
        s = s + "\n"
        for i in range(numOfCols):
                if i != 0:
                        s = s + ","
                s = s + example[i].ljust(maxs[i])
        return s

def getSupported():
        s = "Pin Styles\n"
        for i in range(KiApiItemCont.numOfAvailPinStyles):
                s = s + "    " + KiApiItemCont.availPinStyles[i] + "\n"
        s = s + "\n"

        s = s + "Pin Types\n"
        for i in range(KiApiItemCont.numOfAvailPinTypes):
                s = s + "    " + KiApiItemCont.availPinTypes[i] + "\n"
        s = s + "\n"

        s = s + "Pin Positions\n"
        for i in range(KiApiItemCont.numOfAvailPinPoss):
                s = s + "    " + KiApiItemCont.availPinPoss[i] + "\n"

        return s

try:
        args, vals = getopt.getopt(g_argList, g_opts, g_longOpts)

        for currentArg, currentVal in args:
                currentArg = currentArg.replace(" ", "")
                currentVal = currentVal.replace(" ", "")
                if currentArg in ("-h", "--help"):
                        print("Available options\n"
                        " --help          , -h : Displays this help\n"
                        " --pinNumbers    , -p : Optional. Show pin numbers if this parameter is passed.\n"
                        " --justLib       , -j : Optional. Generate just library if this parameter is passed. Otherwise full project\n"
                        " --logFolderPath , -l : Mandatory. Where log files are going to be stored.\n"
                        " --csvFilePath   , -c : Mandatory. Csv file path\n"
                        " --outFolderPath , -o : Mandatory. Where generated output files are going to be stored.\n"
                        " --pageHeight    , -h : Optional. Default -> " + str(g_args["pageHeight"]) + " \n"
                        " --pageWidth     , -w : Optional. Default -> " + str(g_args["pageWidth"])  + " \n"
                        "\n"
                        + getSupported() +
                        "\n"
                        + getCsvFileExample())
                        exit(0)
                elif currentArg in ("-c", "--csvFilePath"):
                        absPath = os.path.abspath(currentVal)
                        if not os.path.exists(absPath):
                                print(str(absPath) + " not exists.")
                                exit(1)
                        g_args["csvFilePath"] = absPath
                elif currentArg in ("-o", "--outFolderPath"):
                        absPath = os.path.abspath(currentVal)
                        if not os.path.exists(absPath):
                                print(str(absPath) + " not exists.")
                                exit(1)
                        g_args["outFolderPath"] = absPath
                elif currentArg in ("-l", "--logFolderPath"):
                        absPath = os.path.abspath(currentVal)
                        if not os.path.exists(absPath):
                                print(str(absPath) + " not exists.")
                                exit(1)
                        g_args["logFolderPath"] = absPath
                elif currentArg in ("-w", "--pageWidth"):
                        if not currentVal.isnumeric():
                                print("Page width(" + currentVal + ") is not numeric.")
                                exit(1)
                        g_args["pageWidth"] = int(currentVal)
                elif currentArg in ("-h", "--pageHeight"):
                        if not currentVal.isnumeric():
                                print("Page height(" + currentVal + ") is not numeric.")
                                exit(1)
                        g_args["pageHeight"] = int(currentVal)
                elif currentArg in ("-p", "--pinNumbers"):
                        g_args["pinNumbers"] = True
                elif currentArg in ("-j", "--justLib"):
                        g_args["justLib"] = True

except getopt.error as err:
    print("Unrecognized input parameter " + str(err))
    exit(1)

if g_args["csvFilePath"] == None:
        print("Csv file path is not given.")
        exit(1)

if g_args["outFolderPath"] == None:
       print("Output folder is not given.")
       exit(1)

if g_args["logFolderPath"] == None:
        print("Log folder path is not given.")
        exit(1)

api = KiApi(csvFilePath=g_args["csvFilePath"],
            logFolderPath=g_args["logFolderPath"],
            outFolderPath=g_args["outFolderPath"],
            showPinNumbers=g_args["pinNumbers"])

g_genFiles = None
if g_args["justLib"]:
        g_genFiles = api.genLib()
else:
        g_genFiles = api.genPrj(g_args["pageHeight"], g_args["pageWidth"])

for i in range(len(g_genFiles)):
        print("Gen: " + str(g_genFiles[i]))