import re

# qode regx groups 1=qid 2=quadrant _/^  3=postag
QN = re.compile(r'q(\d+)(n|e|r|o|s)_?\^?([A-Z]+)?', re.I) # q1n_POS format
NEWLINE = re.compile(r'[\n\r]+')
NEWLINE2 = re.compile(r'[\n\r]{3,}')
WIKI = re.compile(r'https?://en.wiki(pedia|quote).org/wiki/(.*)') # wikify

# COLORS
GRAYS = [f'{i}{i}{i}{i}{i}{i}' for i in list(range(1, 10))+['A', 'B', 'C', 'D', 'E', 'F']]
SHADES = {
    70: 'Gold',
    65: 'Orange',
    60: 'DarkOrange',
    55: 'Coral',
    50: 'Tomato',
    45: 'OrangeRed',
    40: 'Red',
    35: 'Crimson',
    30: 'IndianRed',
    25: 'Firebrick',
    20: 'DarkRed',
    18: 'Peru',
    16: 'Chocolate',
    14: 'SaddleBrown',
    12: 'Sienna',
    10: 'Brown',
    8: 'Maroon',
    6: 'DarkGray',
    4: 'Gray',
    2: 'DarkSlateGray',
    0: 'DimGray'
}

# POLYNYM MULTI-TERM SYSTEMS
BENNETT = {
    1: 'Monad',
    2: 'Dyad',
    3: 'Triad',
    4: 'Tetrad',
    5: 'Pentad',
    6: 'Hexad',
    7: 'Heptad',
    8: 'Octad',
    9: 'Ennead',
    10: 'Decad',
    11: 'Undecad',
    12: 'Duodecad'
}

# STATUS LEVELS
BADGES = (
    (1000, 'Truth-Fabler'),
    (500, 'Bloctologist'),
    (200, 'High Nymologist'),
    (100, 'Low Nymologist'),
    (50, 'Nymtician'),
    (25, 'Polyanna'),
)
