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

        invertedUniqDict = {v: k for k, v in uniqDict.items()}

        # returns multiples of grid
        def grid(num):
                return num * 1.27

        #       |--------------------------------------------------|
        # lenPin|                                   pinEndToPinName|
        # ↓    ↓|                                                ↓↓|
        # ----->|InPin0                                   outPin0  |-----> ←
        #       |           ↑ spaceBetweenInNOutPin ↑              |       pinToBoxHeight
        #       |--------------------------------------------------|       ←
        # symbol editor constants(only absolute values)
        #
        #   |--------------|   ←
        #   |     OutPin0  |---->←firstPinyOffset
        #   |↑   ↑         |
        #   |spaceBetweenBoxNPinName 
        #   |--------------|
        #
        symEdit = {
                "charHeight"              : grid(1),
                "charWidth"               : grid(1),
                "lenPin"                  : grid(2),
                "spaceBetweenInNOutPin"   : grid(1),
                "spaceBetweenBoxNPinName" : grid(1),
                "heightBetweenPins"       : grid(2),
                "firstPinyOffset"         : grid(3),
                "pinToBoxHeight"          : grid(1),
                "pinEndToPinName"         : grid(1)
        }

        # constants used in log functions
        log = {
                "depthIndentLen" : 4
        }

        # column index in a row in csv file mapping
        csv = {
                "lib"      : 0, # name of the library
                "sym"      : 1, # name of the symbol
                "desig"    : 2, # name of the symbol designator
                "pin"      : 3, # name of the pin
                "pinNumber": 4,
                "pinPos"   : 5, # availPinPoss
                "pinType"  : 6, # availPinTypes
                "pinStyle" : 7, # availPinStyles
                # aka global label
                # if you want to connect multiple global label to pin
                # use delimeter -
                "nodes"    : 8,
                # number of columns
                # if you put more than this amount it will just get ignored
                "count"    : 9
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
                "charWidth"        : grid(1),
                "leftToTextWidth"  : grid(1),
                "rightToTextWidth" : grid(1),
                "height"           : grid(2),
        }

# container that contains single or more global labels called connector.
# a connector is top left aligned.
#
# Module
#---------------------------------------------------------------------------------------------------
# Layouts =>↓ leftConn ↓ leftWire        ↓    symbol                   ↓rightWire↓ rightConn↓
#           x              wirexGap
#           ↓              ↓   ↓
#         y→|----------|                                                         |----------|
#           ||-------\ |                  IC1                                    ||-------\ |
#         C ||        >|---|              |--------------------|             |----|        >|
#         O ||-------/ |   |----          |                    |             |   ||-------/ |
#         N ||-------\ |   |              |                    |         ----|   ||-------\ |
#         N ||        >|---|              |                    |             |---||        >|
#         → ||-------/ |                  |                    |                 ||-------/ |
# connyGap  |----------|                  |                    |                 ||---------|
#         → ||-------\ |                  |                    |                 ||-------\ |
#           ||        >|--------          |                    |         ---------|        >|
#           ||-------/ |                  |                    |                 ||-------/ |
#           |----------|            ----->|                    |---->            |----------|
#                                         |                    |
#                                         |                    |
#                                         |                    |
#                                   ----->|                    |---->
#                                         |--------------------|
        schEdit = {
                "invalidConnIdx"  : -1,
                "connyGap"        : grid(1),
                "connyFirstOffset": grid(1),
                "wirexGap"        : grid(1),
                "moduleyGap"      : grid(2),
                "modulexGap"      : grid(2),
                "desigxOffset"    : 1,
                "desigyOffset"    : 0.2
        }

        # available pin styles
        availPinStyles = [
                "line",
                "clock",
                "clock_low",
                "edge_clock_high",
                "input_low",
                "inverted",
                "inverted_clock",
                "non_logic",
                "output_low"
        ]

        # avaliable pin types
        availPinTypes = [
                "bidirectional",
                "input",
                "output"
        ]

        # avaliable pin positions
        # left or right side of the symbol
        availPinPoss = ["left", "right"]

        numOfAvailPinStyles = len(availPinStyles)
        numOfAvailPinTypes = len(availPinTypes)
        numOfAvailPinPoss = len(availPinPoss)