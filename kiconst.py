class KiConst:
        # purpose of this dictionary :
        # in KiCAD field are name with these certain hashes
        # then this script replaces them and with Jinja magic
        # easy generation
        uniqDict = {
                # lets make it generic, I ll decide on template
                # made sure by x, class does not exist.
                # if correct option not put in template, jinja will fail
                "f135d3a" : "xproject.name",
                "e5ea7ba" : "xlib.name",
                "a87e18d" : "xsym.name",
                "f151dac" : "xsym.designator",
                "f5f9a4a" : "xpin.name",
                "d0035bb" : "xanotherLib.name",
                "d58d89a" : "xanotherSymbol.name",
                "c825b8b" : "xanotherSymbol.designator",
                "d0f82ea" : "xanotherPin.name",
                "c75eb8b" : "xtemp"
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