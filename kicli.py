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

g_args = {
    "csvFilePath" : None,
    "outFolderPath" : None,
    "logFolderPath" : None,
    "pageWidth" : 1366,
    "pageHeight": 768,
    "kicadVersion": "v8", # put here latest that should be default,
    "pinNumbers" : False,
    "fullProject" : False
}
g_argList = sys.argv[1:]
g_opts = "hpfl:c:o:t:h:w:k:"
g_longOpts = ["help", "pinNumbers", "fullProject", "logFolderPath=", "csvFilePath=", "outFolderPath=", "pageHeight=", "pageWidth=", "kicadVersion="]
g_symEditLibs = []
g_prj = None

try:
        args, vals = getopt.getopt(g_argList, g_opts, g_longOpts)

        for currentArg, currentVal in args:
                currentArg = currentArg.replace(" ", "")
                currentVal = currentVal.replace(" ", "")
                if currentArg in ("-h", "--help"):
                        print("Available options\n"
                        " --help          , -h : Displays this help\n"
                        " --pinNumbers    , -p : Optional. Show pin numbers if this parameter is passed.\n"
                        " --fullProject   , -f : Optional. Create only library if this parameter is passed.\n"
                        " --logFolderPath , -l : Mandatory. Where log files are going to be stored.\n"
                        " --csvFilePath   , -c : Mandatory. Csv file path\n"
                        " --outFolderPath , -o : Mandatory. Where generated output files are going to be stored.\n"
                        " --pageHeight    , -h : Optional. Default -> " + str(g_args["pageHeight"]) + " \n"
                        " --pageWidth     , -w : Optional. Default -> " + str(g_args["pageWidth"])  + " \n"
                        " --kicadVersion  , -k : Optional. Default -> " + g_args["kicadVersion"] + " \n")
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
                elif currentArg in ("-k", "--kicadVersion"):
                        g_args["kicadVersion"] = currentVal
                elif currentArg in ("-p", "--pinNumbers"):
                        g_args["pinNumbers"] = True
                elif currentArg in ("-f", "--fullProject"):
                        g_args["fullProject"] = True

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
            kicadVersion=g_args["kicadVersion"],
            showPinNumbers=g_args["pinNumbers"])

if g_args["fullProject"]:
        api.genPrj(g_args["pageHeight"], g_args["pageWidth"])
else:
        api.genLib()