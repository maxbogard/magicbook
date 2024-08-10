"""
this is a temporary file
anything here should be moved to a config file at some point
"""

SPLITSORT = {
    2: [
        {"parts": [1, 1, 1], "name": "1"},
        {"parts": [2, 2, 2], "name": "2"},
    ],
    3: [
        {"parts": [1, 1, 1], "name": "1"},
        {"parts": [1, 2, 2], "name": "2A"},
        {"parts": [2, 2, 2], "name": "2B"},
        {"parts": [2, 3, 3], "name": "3"}
    ],
    4: [
        {"parts": [1, 1, 1], "name": "1"},
        {"parts": [1, 1, 2], "name": "2A"},
        {"parts": [1, 2, 2], "name": "2B"},
        {"parts": [2, 2, 2], "name": "2C"},
        {"parts": [2, 2, 3], "name": "3A"},
        {"parts": [2, 3, 3], "name": "3B"},
        {"parts": [2, 3, 4], "name": "4"}
    ]
}

# Paper Sizes

LYRE_PAPER_X = 504
LYRE_PAPER_Y = 345.6

LYRE_CONTENT_X = 475.2
LYRE_CONTENT_Y = 345.6

LYRE_MARGIN_X = 10
LYRE_MARGIN_TOP = 6
LYRE_MARGIN_BOTTOM = 10

LETTER_MARGIN_X = 10
LETTER_MARGIN_Y = 10

PAGE_FORMATS = ['PORTRAIT', 'LYRE']

MARCHPACK_FORMATS = ('MarchpackSplit', 'MarchpackComprehensive')
BINDER_FORMATS = ('BinderOnePartPg',
                  'BinderOneChartPg',
                  'BinderSaveSomePaper',
                  'BinderSaveLotsPaper'
                  )
