from kiconst import KiConst

class KiUtil:
        # used for pretty printing of parsed csv structure
        def getInfoDepthStr(depth, pos):
                s = ""
                if depth != 0:
                        if depth > 1:
                                s = s + " " * (depth-1) * KiConst.INFO_SINGLE_DEPTH_INDENT_LEN
                        s = s + str(pos) + ("-" * (KiConst.INFO_SINGLE_DEPTH_INDENT_LEN-1)) + "|"
                else:
                        s = "|"
                return s