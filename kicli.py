import csv
import sys
import os
import getopt

g_dirPath = os.path.abspath(sys.argv[0])
g_dirPath = os.path.dirname(g_dirPath)
g_prjPath = g_dirPath
sys.path.append(g_prjPath)
sys.path.append(os.path.join(g_prjPath, "sources"))

from kiprj import KiPrj
from kisymedit import KiSymEditLib
from kischedit import KiSchEditPrj
from kipro import KiPro
from kiutil import KiUtil
from kisymlibtable import KiSymLibTable
from kiprl import KiPrl

g_args = {
    "csvFilePath" : None,
    "outFolderPath" : None,
    "logFolderPath" : None,
    "pageWidth" : 0,
    "pageHeight": 0,
    "kicadVersion": "v8" # put here latest that should be default
}
g_argList = sys.argv[1:]
g_opts = "hl:c:o:t:h:w:k:"
g_longOpts = ["help", "logFolderPath=", "csvFilePath=", "outFolderPath=", "pageHeight=", "pageWidth=", "kicadVersion="]
g_symEditLibs = []
g_prj = None

try:
        args, vals = getopt.getopt(g_argList, g_opts, g_longOpts)

        for currentArg, currentVal in args:
                currentArg = currentArg.replace(" ", "")
                currentVal = currentVal.replace(" ", "")
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

if g_args["pageWidth"] == 0:
        print("Page width is not given.")
        exit(1)

if g_args["pageHeight"] == 0:
        print("Page height is not given.")
        exit(1)

g_equivalentVersion = ""
g_templateDir = None
try:
        lookupTablePath = os.path.join(g_prjPath, "templates/version_lookup_table.csv")
        with open(lookupTablePath) as file:
                for line in file:
                        items = line.split(',')
                        if items[0][0] == "#":
                                continue
                        if len(items) != 2:
                                print(str(lookupTablePath))
                                print("number of items in a given line should be 2 " + line)
                                exit(1)
                        if items[0] == g_args["kicadVersion"]:
                                g_equivalentVersion = items[1]
                                break
except Exception as e:
        print(str(os.path.join(g_prjPath, "templates/version_lookup_table.csv")))
        print(e)
        exit(1)

if g_equivalentVersion == "":
        print("can not find equivalent version in lookup table")
        exit(1)
else:
        absPath = os.path.join(g_prjPath, "templates/" + g_equivalentVersion)
        if not os.path.exists(absPath):
                print("templates does not exist for that version requested " \
                      + g_args["kicadVersion"] + " equivalent " + g_equivalentVersion)
                print("looked for templates here->" + str(absPath))
                exit(1)
        g_templateDir = absPath

g_prj = KiPrj(g_args["logFolderPath"])
g_prj.parseFromCsv(g_args["csvFilePath"])
g_prj.log()

# we always parse for symbol editor. even if it is not used directly; sch editor will use it
for i in range(g_prj.numOfLibs):
        symEditLib = KiSymEditLib(g_args["logFolderPath"])
        symEditLib.parse(g_prj.name, g_prj.libs[i])
        g_symEditLibs.append(symEditLib)

g_absPath = None

for i in range(len(g_symEditLibs)):
        g_absPath = os.path.join(g_templateDir, "e5ea7ba.kicad_sym")
        g_symEditLibs[i].gen(g_absPath, g_args["outFolderPath"])

g_absPath = os.path.join(g_templateDir, "f135d3a.kicad_sch")
g_schEditPrj = KiSchEditPrj(g_args["logFolderPath"])
g_retVal = g_schEditPrj.parse(g_prj.name, g_symEditLibs, g_args["pageWidth"], g_args["pageHeight"])
if g_retVal == False:
        print("WARN: Project(" + g_prj.name + ") did not fit into page.")
g_schEditPrj.gen(g_absPath, g_args["outFolderPath"])

g_absPath = os.path.join(g_templateDir, "f135d3a.kicad_pro")
g_pro = KiPro(g_prj.name)
g_pro.gen(g_absPath, g_args["outFolderPath"])

g_absPath = os.path.join(g_templateDir, "f135d3a.kicad_prl")
g_pro = KiPrl(g_prj.name)
g_pro.gen(g_absPath, g_args["outFolderPath"])

g_absPath = os.path.join(g_args["outFolderPath"], g_prj.name + ".kicad_pcb")
KiUtil.copyPaste(os.path.join(g_templateDir, "f135d3a.kicad_pcb"),
                g_absPath)
print("Copy To: " + str(g_absPath))

g_absPath = os.path.join(g_templateDir, "sym-lib-table")
g_pro = KiSymLibTable(g_prj)
g_pro.gen(g_absPath, g_args["outFolderPath"])

