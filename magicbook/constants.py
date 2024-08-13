"""
this is NOT a temporary file
but anything here should only be used to create an initial
config.json file
"""

DEFAULT_CONFIG = {
  "directories": {
    "ensembles": "ensembles",
    "templates": "templates",
    "schema": "schema",
    "library": "music-library",
    "output": "output",
    "logs": "logs"
  },
  "default-ensemble": "generic_ensemble.json",
  "default-instruments": "instruments.json",
  "paper-sizes": {
    "Marchpack": {
      "width": 504,
      "height": 345.6,
      "right-offset:": 28.8
    }
  }
}

DEFAULT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Chart",
    "description": "Sheet music containing one or more songs",
    "type": "object",
    "properties": {
        "slug": {
            "description": "The name of the diretory this chart is stored in",
            "type": "string"
        },
        "title": {
            "description": "The title of the chart, not necessary when"
            " the chart only contains one chart",
            "type": "string"
        },
        "songs": {
            "description": "Songs that are included on this chart",
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {
                        "description": "the title of the song",
                        "type": "string"
                    },
                    "artist": {
                        "description": "the artist the song is most commonly "
                        "associated with",
                        "type": "string"
                    },
                    "arranger": {
                        "description": "the arranger of the song",
                        "type": "string"
                    }
                },
                "minItems": 1,
                "uniqueItems": True
            }
        }
    },
    "required": ["slug", "songs"]
}

DEFAULT_INSTRUMENTS = {
  "piccolo": {
    "name": "Flute",
    "family": "woodwind",
    "div": 1,
    "key": "concert",
    "alternates": ["flute", "keyboards"]
  },
  "flute": {
    "name": "Flute",
    "family": "woodwind",
    "div": 1,
    "key": "concert",
    "alternates": ["piccolo", "keyboards"]
  },
  "oboe": {
    "name": "Oboe",
    "family": "woodwind",
    "div": 1,
    "key": "concert",
    "alternates": ["flute", "keyboards", "piccolo"]
  },
  "bassoon": {
    "name": "Bassoon",
    "family": "woodwind",
    "div": 1,
    "key": "concert",
    "alternates": ["baritonebc", "trombone", "bassguitar", "tuba"]
  },
  "clarinet": {
    "name": "Clarinet",
    "family": "woodwind",
    "div": 2,
    "key": "Bb",
    "alternates": ["sopranosax", "trumpet", "tenorsax"]
  },
  "clarbass": {
    "name": "Bass Clarinet",
    "family": "woodwind",
    "div": 1,
    "key": "Bb",
    "alternates": ["tenorsax", "baritonetc"]
  },
  "sopranosax": {
    "name": "Soprano Sax",
    "family": "saxophone",
    "div": 1,
    "key": "Bb",
    "alternates": ["clarinet", "trumpet", "tenorsax"]
  },
  "altosax:": {
    "name": "Alto Sax",
    "family": "saxophone",
    "div": 1,
    "key": "Eb"
  },
  "tenorsax": {
    "name": "Tenor Sax",
    "family": "saxophone",
    "div": 1,
    "key": "Bb",
    "alternates": ["baritonetc", "bassclarinet", "sopranosax", "trumpet"]
  },
  "barisax": {
    "name": "Bari Sax",
    "family": "saxophone",
    "div": 1,
    "key": "Eb",
    "alternates": ["bassguitar", "tuba", "baritonebc", "trombone", "altosax"]
  },
  "trumpet": {
    "name": "Trumpet",
    "family": "highbrass",
    "div": 3,
    "key": "Bb",
    "alternates": ["sopranosax", "slarinet", "tenorsax"]
  },
  "hornf": {
    "name": "F Horn",
    "family": "highbrass",
    "div": 1,
    "key": "F",
    "alternates": []
  },
  "trombone": {
    "name": "Trombone",
    "family": "lowbrass",
    "div": 2,
    "key": "bc",
    "alternates": ["baritonebc", "bassguitar", "tuba"]
  },
  "baritonebc": {
    "name": "Baritone BC",
    "family": "lowbrass",
    "div": 1,
    "key": "bc",
    "alternates": ["trombone", "bassguitar", "tuba"]
  },
  "baritonetc": {
    "name": "Baritone TC",
    "family": "lowbrass",
    "div": 1,
    "key": "Bb",
    "alternates": ["tenorsax", "bassclarinet"]
  },
  "tuba": {
    "name": "Tuba",
    "family": "lowbrass",
    "div": 1,
    "key": "bc",
    "alternates": ["bassguitar", "baritonebc", "trombone"]
  },
  "keyboards": {
    "name": "Keyboards",
    "family": "percussion",
    "div": 1,
    "key": "concert",
    "alternates": ["flute", "piccolo", "oboe"]
  },
  "bassguitar": {
    "name": "Bass Guitar",
    "family": "rhythm",
    "div": 1,
    "key": "bc",
    "alternates": ["tuba", "baritonebc", "barisax"]
  },
  "drumset": {
    "name": "Drumset",
    "family": "rhythm",
    "div": 1,
    "key": "percussion",
    "alternates": [
      "snaredrum",
      "multitoms",
      "bassdrum",
      "bassguitar",
      "tuba",
      "trumpet"
    ]
  },
  "snaredrum": {
    "name": "Snare Drum",
    "family": "drumline",
    "div": 1,
    "key": "percussion",
    "alternates": [
      "drumset",
      "multitoms",
      "bassdrum",
      "bassguitar",
      "tuba",
      "trumpet"
    ]
  },
  "multitoms": {
    "name": "Multi-Toms",
    "family": "drumline",
    "div": 1,
    "key": "percussion",
    "alternates": [
      "snaredrum",
      "drumset",
      "bassdrum",
      "bassguitar",
      "tuba",
      "trumpet"
    ]
  },
  "bassdrum": {
    "name": "Bass Drum",
    "family": "drumline",
    "div": 1,
    "key": "percussion",
    "alternates": [
      "drumset",
      "cymbals",
      "snaredrum",
      "multitoms",
      "bassguitar",
      "tuba",
      "trumpet"
    ]
  },
  "cymbals": {
    "name": "Cymbals",
    "family": "drumline",
    "div": 1,
    "key": "percussion",
    "alternates": [
      "bassdrum",
      "drumset",
      "snaredrum",
      "multitoms",
      "bassguitar",
      "tuba",
      "trumpet"
    ]
  }
}

DEFAULT_ENSEMBLE = {
  "name": "My Community Band",
  "slug": "mcband",
  "instruments": [
    {
      "slug": "flute",
      "name": "Flute",
      "div": 1
    },
    {
      "slug": "clarinet",
      "name": "Clarinet",
      "div": 2
    },
    {
      "slug": "altosax",
      "name": "Alto Sax",
      "div": 1
    },
    {
      "slug": "tenorsax",
      "name": "Tenor Sax",
      "div": 1
    },
    {
      "slug": "barisax",
      "name": "Bari Sax",
      "div": 1
    },
    {
      "slug": "trumpet",
      "name": "Trumpet",
      "div": 3
    },
    {
      "slug": "hornf",
      "name": "F Horn",
      "div": 1
    },
    {
      "slug": "trombone",
      "name": "Trombone",
      "div": 2
    },
    {
      "slug": "baritonebc",
      "name": "Baritone BC",
      "div": 1
    },
    {
      "slug": "baritonetc",
      "name": "Baritone TC",
      "div": 1
    },
    {
      "slug": "tuba",
      "name": "Tuba",
      "div": 1
    },
    {
      "slug": "keyboards",
      "name": "Keyboards",
      "div": 1
    },
    {
      "slug": "bassguitar",
      "name": "Bass Guitar",
      "div": 1
    },
    {
      "slug": "drumset",
      "name": "Drum Set",
      "div": 1
    },
    {
      "slug": "snaredrum",
      "name": "Snare Drum",
      "div": 1
    },
    {
      "slug": "multitoms",
      "name": "Multi Toms",
      "div": 1
    },
    {
      "slug": "bassdrum",
      "name": "Bass Drum",
      "div": 1
    },
    {
      "slug": "cymbals",
      "name": "Cymbals",
      "div": 1
    }
  ]
}


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
