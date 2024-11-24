from kiconst import KiConst
from kiutil import KiUtil
from kilib import *
import csv
import os

class KiPrj:
        def __init__(self):
                self.name = ""
                self.numOfLibs = 0
                self.libs = [] # class KiLib type

        def parseFromCsv(self, csvFilePath):
                self.name = str(os.path.basename(csvFilePath)).replace(".csv", "")
                with open(csvFilePath, newline='') as csvFile:
                        csvReader = csv.reader(csvFile)
                        rowList = []
                        for row in csvReader:
                                if row[0][0] == "#":
                                        continue
                                rowList.append(row)
                        # if empty just return
                        if len(rowList) == 0:
                                return

                        lastLibName = ""
                        lastRowIdx = []
                        # deducing entry and exit boundary of a library in csv file
                        for i in range(len(rowList)):
                                # creating new library for every different library name found in csv file
                                if rowList[i][KiConst.CSV_COL_LIB_NAME] != lastLibName:
                                        kiLib = KiLib()
                                        self.libs.append(kiLib)
                                        # storing idx that I found different library name
                                        lastRowIdx.append(i)
                                        lastLibName = rowList[i][KiConst.CSV_COL_LIB_NAME]
                        self.numOfLibs = len(self.libs)
                        # for loop wont detect last item library name change so added myself
                        lastRowIdx.append(len(rowList))

                        for i in range(self.numOfLibs):
                                # parsing library with entry and exit boundary
                                self.libs[i].parseFromCsv(rowList[lastRowIdx[i] : lastRowIdx[i+1]])


        def log(self, depth, pos):
                s = KiUtil.getLogDepthStr(depth, pos) + self.name + " " + str(self.numOfLibs) + "\n"
                for i in range(self.numOfLibs):
                        s = s + self.libs[i].log(depth + 1, i + 1)
                return s

