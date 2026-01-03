#!/usr/bin/env python
# encoding: utf-8
'''
cached.py -- Nymology cached startup data
'''
import re

# qode regx groups 1=qid 2=quadrant _/^  3=postag
QN = re.compile(r'q(\d+)(n|e|r|o|s)_?\^?([A-Z]+)?', re.I) # q1n_POS
QTAG = re.compile(r'(q\d+(n|e|r|o|s)_?\^?([A-Z]+)?)', re.I) # q1n_POS/whole tag
NEWLINE = re.compile(r'[\n\r]+')
NEWLINE2 = re.compile(r'[\n\r]{3,}')
WIKI = re.compile(r'https?://en.wiki(pedia|quote).org/wiki/(.*)') # wikify

# COLORS
GAMES = {
    'QuizZection': 'Indigo',
    'PolyPuzzle': 'Plum',
    'QuadraZone': 'LightSeaGreen',
    'unQuote': 'Peru',
    'TheGist': 'DeepSkyBlue',
}
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
FEEL_SITE = {
    'areas': ['Linguistics', 'Philosophy', 'Physics', 'Semiotics'],
    'deps': ['2', '3', '<b>4</b><sub>2</sub>'],
    'freq': [('science', 52), ('explanation', 27), ('grammar', 10), ('circuit', 3)],
    'maxcount': 52,
    'nams': ['science', 'explanation', 'grammar', 'circuit'],
    'poly_ids': [22, 49, 57, 149],
    'sources': ['Arthur Schopenhauer', 'Charles Peirce', 'Noam Chomsky', 'electrical'],
    'terms': ['becoming', 'being', 'context-free', 'context-sensitive', 'discovery', 'knowing', 'parallel',
           'practical', 'recursively enumerable', 'regular', 'series', 'theoretical', 'willing'],
    'url': 'https://en.wikipedia.org/wiki/Logic',
}
def badge(totalscore):
    'user status'
    if not totalscore > BADGES[0][0]:
        nextlevel = BADGES[-1][0]
        for level, (threshold, badj) in enumerate(BADGES):
            if totalscore > threshold:
                return badj, nextlevel, level
            nextlevel = threshold - totalscore
        return 'Nym Noob', nextlevel, 6
    return BADGES[0][1], None, 0

def shade(level):
    'level hue'
    hue = SHADES.get(level-level%2)
    hue = SHADES.get(level-level%5) if not hue else hue
    return ('GreenYellow' if level > 74 else 'DimGray') if not hue else hue
