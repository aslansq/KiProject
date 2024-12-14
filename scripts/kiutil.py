from kiconst import KiConst
import uuid

class KiUtil:
        # used for pretty printing of parsed csv structure
        def getLogDepthStr(depth, pos):
                s = ""
                if depth != 0:
                        if depth > 1:
                                s = s + " " * (depth-1) * KiConst.log["depthIndentLen"]
                        s = s + str(pos) + ("-" * (KiConst.log["depthIndentLen"]-1)) + "|"
                else:
                        s = "|"
                return s

        def copyPaste(srcPath, dstPath):
                with open(srcPath, 'r') as srcFile:
                        with open(dstPath, 'w') as dstFile:
                                for srcLine in srcFile:
                                        dstFile.write(srcLine)

        def roundToGrid(num):
                return KiConst.grid(1) * round(num/KiConst.grid(1))

        def getUuid(s):
                myUuid = uuid.UUID('{12345678-1234-5678-1234-567812345678}')
                return str(uuid.uuid3(myUuid, s))

        def removeEmptyLines(s):
                r = ""
                for l in s.split("\n"):
                        if l != "":
                                r = r + l + "\n"
                return r