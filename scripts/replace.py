import os
import sys
import glob

g_dirPath = os.path.abspath(sys.argv[0])
g_dirPath = os.path.dirname(g_dirPath)
g_prjPath = os.path.join(g_dirPath, "..")
sys.path.append(g_prjPath)

from kiconst import KiConst

# where replaced files will be stored
g_devFolderPath = os.path.abspath(os.path.join(g_prjPath, "dev"))
# where is KiCAD project
g_origFolderPath = os.path.abspath(os.path.join(g_prjPath, "project"))

g_origFilePaths = []
# recursively walk original project
for path in glob.glob(os.path.abspath(os.path.join(g_origFolderPath, "**")), recursive=True):
        fileName = os.path.basename(path)
        # ignore backup files
        if os.path.isfile(path) and (not "backups" in str(path)) and (not ".bak" in fileName):
                g_origFilePaths.append(os.path.abspath(path))

g_dstFilePaths = []
for oPath in g_origFilePaths:
        # convert to string for manipulation
        oPath = str(oPath)
        # change orig folder path to dev folder path which destination
        oPath = oPath.replace(str(g_origFolderPath), str(g_devFolderPath))
        # convert back to path
        oPath = os.path.abspath(oPath)
        g_dstFilePaths.append(oPath)

for i in range(len(g_origFilePaths)):
        origFilePath = g_origFilePaths[i]
        dstFilePath = g_dstFilePaths[i]
        dstFolderPath = os.path.dirname(dstFilePath)
        # since we walked project folder recursively, if folder does not exist in dev then create
        if not os.path.exists(dstFolderPath):
                os.makedirs(dstFolderPath)

        inFile = None
        outFile = None
        try:
                inFile = open(origFilePath, "r", encoding="utf8")
                outFile = open(dstFilePath, "w", encoding="utf8")
        except Exception as e:
                print(e)
                continue

        print("#"*120)
        print("replacing -> " + str(origFilePath))
        lineNumber = 1
        for line in inFile:
                keyFound = False
                for key in KiConst.uniqDict:
                        value = KiConst.uniqDict[key]
                        if key in line:
                                line = line.replace(key, "{{"+ value + "}}") # put it as jinja var
                                keyFound = True
                if keyFound:
                        # let me know what do I need replace bare minimum
                        print(str(lineNumber) + " " + line.replace(" ", "").replace("\t", ""))
                outFile.write(line)
                lineNumber = lineNumber + 1
        print("\n")

        if inFile != None:
                inFile.close()
        if outFile != None:
                outFile.close()
