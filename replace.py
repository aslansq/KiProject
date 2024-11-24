import os
import sys
import glob
from kiconst import KiConst

# where replaced files will be stored
devFolderPath = os.path.abspath('./dev')
# where is KiCAD project
origFolderPath = os.path.abspath('./project')

origFilePaths = []
# recursively walk original project
for path in glob.glob(os.path.abspath(os.path.join(origFolderPath, "**")), recursive=True):
        fileName = os.path.basename(path)
        # ignore backup files
        if os.path.isfile(path) and (not "backups" in str(path)) and (not ".bak" in fileName):
                origFilePaths.append(os.path.abspath(path))

dstFilePaths = []
for oPath in origFilePaths:
        # convert to string for manipulation
        oPath = str(oPath)
        # change orig folder path to dev folder path which destination
        oPath = oPath.replace(str(origFolderPath), str(devFolderPath))
        # convert back to path
        oPath = os.path.abspath(oPath)
        dstFilePaths.append(oPath)

for i in range(len(origFilePaths)):
        origFilePath = origFilePaths[i]
        dstFilePath = dstFilePaths[i]
        dstFolderPath = os.path.dirname(dstFilePath)
        # since we walked project folder recursively, if folder does not exist in dev then create
        if not os.path.exists(dstFolderPath):
                os.makedirs(dstFolderPath)
        # start replacing
        with open(origFilePath, "r", encoding="utf8") as inFile:
                with open(dstFilePath, "w", encoding="utf8") as outFile:
                        for line in inFile:
                                for key in KiConst.uniqDict:
                                        value = KiConst.uniqDict[key]
                                        line = line.replace(key, "{{"+ value + "}}") # put it as jinja var
                                outFile.write(line)
