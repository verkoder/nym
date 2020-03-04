#!/usr/bin/env python
# encoding: utf-8
'''
do_wiki.py -- Nymology wikipedia tools
'''
from random import choice, sample
import wikipedia

WAYS = ('part', 'step', 'type', 'kind', 'way', 'method', 'style')
NUMS = ('two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve')


def wiki_url(name, area):
    'guess wikipedia URL --UNUSED: so-so results'

    try:
        page = wikipedia.page(name) # first try "name"
    except (wikipedia.DisambiguationError, wikipedia.exceptions.PageError):

        try:                             # then try "name (area)"
            page = wikipedia.page(f'{name} ({area.lower()})')
        except (wikipedia.DisambiguationError, wikipedia.exceptions.PageError):
            return

    return page.url

def suggest_poly(Polynym):
    'suggest polynym to-do --DEPRECATED: BAD RESULTS!'

    # search wikipedia API
    got = wikipedia.search(f'{choice(NUMS)} {choice(WAYS)}s', 20)

    # remove film/albums/etc
    got = [x.replace(' ', '_') for x in got if not x.startswith('IEC')
           and not x.startswith('ISO')
           and 'film' not in x
           and 'album' not in x]
    got = [f'https://en.wikipedia.org/wiki/{x}' for x in got]

    # remove seen URLs
    dupes = [x.wiki for x in Polynym.objects.filter(wiki__in=got)]
    got = sample(list(set(got) - set(dupes)), 5)

    return [(x, x[30:].replace('_', ' ')) for x in got]

def suggest_polys(Polynym, num):
    'suggest polynyms to-do --DEPRECATED: BAD RESULTS!'

    return [y for x in [suggest_poly(Polynym) for x in range(num)] for y in x]
