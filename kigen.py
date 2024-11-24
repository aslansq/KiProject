import csv
import sys
import os
import getopt
from kiprj import KiPrj
from kisymedit import KiSymEditLib
from kischedit import KiSchEditPrj

g_args = {
    "csvFilePath" : None,
    "outFolderPath" : None,
    "infoFlag" : False,
    "templateFilePath" : None
}
g_argList = sys.argv[1:]
g_opts = "hic:o:t:"
g_longOpts = ["help", "info", "csvFilePath=", "outFolderPath=", "templateFilePath="]

try:
        args, vals = getopt.getopt(g_argList, g_opts, g_longOpts)

        for currentArg, currentVal in args:
                currentArg = currentArg.replace(" ", "")
                if currentArg in ("-h", "--help"):
                        print("Available options\n"
                        " --help        , -h : Displays this help\n"
                        " --csvFilePath , -c : Csv file path\n")
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
                elif currentArg in ("-o", "--info"):
                        g_args["infoFlag"] = True
                elif currentArg in ("-t", "--templateFilePath"):
                        absPath = os.path.abspath(currentVal)
                        if not os.path.exists(absPath):
                                print(str(absPath) + " not exists.")
                                exit(1)
                        g_args["templateFilePath"] = absPath

except getopt.error as err:
    print("Unrecognized input parameter " + str(err))
    exit(1)

if g_args["csvFilePath"] == None:
        print("Csv file path is not given.")
        exit(1)

if g_args["outFolderPath"] == None:
       print("Output folder is not given.")
       exit(1)

if g_args["templateFilePath"] == None:
        print("Template file is not given.")
        exit(1)

kiPrj = KiPrj()
kiPrj.parseFromCsv(g_args["csvFilePath"])
if g_args["infoFlag"]:
        with open(os.path.join(g_args["outFolderPath"], "info.txt"), "w") as infoFile:
                infoFile.write(kiPrj.info(0, 1))

if "kicad_sym" in g_args["templateFilePath"]:
        for i in range(kiPrj.numOfLibs):
                kiSymEditLib = KiSymEditLib()
                kiSymEditLib.parse(kiPrj.libs[i])
                kiSymEditLib.gen(g_args["templateFilePath"], g_args["outFolderPath"])
else:
        kiSchEditPrj = KiSchEditPrj()
        kiSchEditPrj.parse(kiPrj)
        kiSchEditPrj.gen(g_args["templateFilePath"], g_args["outFolderPath"])