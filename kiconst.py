class KiConst:
        # purpose of this dictionary :
        # in KiCAD field are name with these certain hashes
        # then this script replaces them and with Jinja magic
        # easy generation
        uniqDict = {
                "f135d3a" : "project.name",
                "e5ea7ba" : "lib.name",
                "a87e18d" : "symbol.name",
                "f151dac" : "symbol.designator",
                "f5f9a4a" : "pin.name",
                "d0035bb" : "pin.type",
                "b4641fc" : "pin.dir",
                "c75eb8b" : "temp"
        }
        #                                             pinToBoxWidth
        #                                                      ↓  ↓
        #   |--------------------------------------------------|
        # lenPin                              pinEndToPinName  |
        # ↓ |  ↓                                        ↓   ↓  |
        # -----> InPin0                           outPin0    -----> ←
        #   |           ↑ spaceBetweenInNOutPin ↑              |     pinToBoxHeight
        #   |--------------------------------------------------|    ←
        # symbol editor constants(only absolute values)
        #
        #   |--------------|   ←
        #   |     OutPin0 ---->←firstPinyOffset
        #   |↑   ↑         |
        #   |spaceBetweenBoxNPinName
        #   |--------------|
        #
        symEdit = {
                "charHeight"              : 1.27,
                "charWidth"               : 1.27,
                "lenPin"                  : 2.54,
                "spaceBetweenInNOutPin"   : 0.1,
                "spaceBetweenBoxNPinName" : 1,
                "heightBetweenPins"       : 1.8,
                "firstPinyOffset"         : 3,
                "pinToBoxWidth"           : 1.01,
                "pinToBoxHeight"          : 1.01,
                "pinEndToPinName"         : 0.7
        }

        invertedUniqDict = {v: k for k, v in uniqDict.items()}

        INFO_SINGLE_DEPTH_INDENT_LEN = 4
        # never change order of columns
        CSV_COL_LIB_NAME = 0
        CSV_COL_SYM_NAME = 1
        CSV_COL_SYM_DESIG = 2
        CSV_COL_PIN_NAME = 3
        CSV_COL_PIN_DIR = 4
        CSV_COL_PIN_STYLE = 5
        CSV_COL_PIN_NODES = 6
        CSV_COL_COUNT = 7