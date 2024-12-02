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
    "logFolderPath" : None,
    "templateFilePath" : None
}
g_argList = sys.argv[1:]
g_opts = "hl:c:o:t:"
g_longOpts = ["help", "logFolderPath=", "csvFilePath=", "outFolderPath=", "templateFilePath="]
g_symEditLibs = []
g_prj = None

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
                elif currentArg in ("-l", "--logFolderPath"):
                        absPath = os.path.abspath(currentVal)
                        if not os.path.exists(absPath):
                                print(str(absPath) + " not exists.")
                                exit(1)
                        g_args["logFolderPath"] = absPath
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

if g_args["logFolderPath"] == None:
        print("Log folder path is not given.")
        exit(1)

g_prj = KiPrj(g_args["logFolderPath"])
g_prj.parseFromCsv(g_args["csvFilePath"])
g_prj.log()

# we always parse for symbol editor. even if it is not used directly; sch editor will use it
for i in range(g_prj.numOfLibs):
        symEditLib = KiSymEditLib(g_args["logFolderPath"])
        symEditLib.parse(g_prj.name, g_prj.libs[i])
        g_symEditLibs.append(symEditLib)

if "kicad_sym" in g_args["templateFilePath"]: # if correct template given gen lib for symbol editor
        for i in range(len(g_symEditLibs)):
                g_symEditLibs[i].gen(g_args["templateFilePath"], g_args["outFolderPath"])

else:
        schEditPrj = KiSchEditPrj(g_args["logFolderPath"])
        schEditPrj.parse(g_prj.name, g_symEditLibs, 192, 108)
        schEditPrj.gen(g_args["templateFilePath"], g_args["outFolderPath"])