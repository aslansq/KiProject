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
                "de51abf" : "xglobalInputLabel.name",
                "fc9d56b" : "xglobalOutputLabel.name",
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
                "heightBetweenPins"       : 2.57,
                "firstPinyOffset"         : 3,
                "pinToBoxWidth"           : 1.01,
                "pinToBoxHeight"          : 1.01,
                "pinEndToPinName"         : 0.7
        }

        invertedUniqDict = {v: k for k, v in uniqDict.items()}

        info = {
                "depthIndentLen" : 4
        }

        csv = {
                "lib"      : 0,
                "sym"      : 1,
                "desig"    : 2,
                "pin"      : 3,
                "pinDir"   : 4,
                "pinStyle" : 5,
                "nodes"    : 6,
                "count"    : 7
        }

        #  leftToTextWidth
        #  ↓   ↓
        #  |----------\  ←
        #  |   text    >    height
        #  |----------/  ←
        #          ↑   ↑
        #          rightToTexWidth
        #
        #                  x
        #     |----------\ ↓
        #     |    in     > ← y
        #     |----------/  ←
        #
        #    x
        #    ↓|----------\   ←
        #  y→ |    out    >    height
        #     |----------/   ←

        globalLabel = {
                "charWidth" : 1.27,
                "leftToTextWidth"          : 1.27,
                "rightToTextWidth"          : 1.55,
                "height"                   : 2.54,
        }

# container that contains single more global labels called connector.
# a connector is top left aligned.
#
# Module
#---------------------------------------------------------------------------------------------------
# Layouts =>↓ inConn   ↓ inWire          ↓    symbol                 ↓ outWire         ↓ outConn ↓
#                       multiNode
#                      ↓                 ↓
#           x                      wirexGap
#           ↓                      ↓     ↓
#         y→|----------|                                                               |----------|
#           ||-------\ |                     IC1                                       ||-------\ |
#         C ||        >|---|                 |--------------------|                |----|        >|
#         O ||-------/ |   |-------|         |                    |                |   ||-------/ |
#         N ||-------\ |   |       |         |                    |   |------------|   ||-------\ |
#         N ||        >|---|       |         |                    |   |            |---||        >|
#         → ||-------/ |           |         |                    |   |                ||-------/ |
# connyGap  |----------|           |         |                    |   |                ||---------|
#         → ||-------\ |           |         |                    |   |                ||-------\ |
#           ||        >|--------|  |         |                    |   |    |------------|        >|
#           ||-------/ |        |  |         |                    |   |    |           ||-------/ |
#           |----------|        |  |----------->                ----->|    |           |----------|
#                               |            |                    |        |
#                               |            |                    |        |
#                               |            |                    |        |
#                               |-------------->                ----->-----|
#                                            |--------------------|
        schEdit = {
                "invalidConnIdx" : -1,
                "connyGap" : 1.27,
                "connyFirstOffset": 1.27,
                "wirexGap" : 1.27,
                "moduleyGap" : 2.54,
                "modulexGap" : 2.54,
                "desigxOffset" : 1,
                "desigyOffset" : 0.2,
                "pageOffset" : 14
        }