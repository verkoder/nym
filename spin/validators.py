#!/usr/bin/env python
# encoding: utf-8
'''
validators.py -- Nymology data validators
'''
from django.core.validators import RegexValidator

from .cached import QN

MODES = (
    ('', '<< Mode >>'),
    ('type', 'Type / Kind / Method'),
    ('part', 'Part / Piece / Area'),
    ('step', 'Step / Stage / Level')
)

POS = (
    ('', '<< Part-of-Speech >>'),
    ('NN', 'Noun (NN)'),
    ('VB', 'Verb (VB)'),
    ('ADJ', 'Adjective (ADJ)')
)

QODER = RegexValidator(regex=QN, message='No topic in Qode!')
