from kiconst import KiConst

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