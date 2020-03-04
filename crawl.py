#!/usr/bin/env python
# encoding: utf-8
"""
crawl.py -- Nymology data crawler/miner
Import Nymbase data from:
  - fortunes.dat -- 3k quotes & fortunes; thanks to bmc@clapper.org
                                    https://github.com/bmc/fortunes
  - quotes.pkl -- via Quotes.net API
"""
import re
import pickle
import requests
from django.db.utils import DataError

from spin.models import Fortune, Quadranym, Quote, thingify, dimension_dict
from nym.keys import QUOTES_API # stands4.com limit @ 100/day

SPACE = re.compile(r'(?s)\s\s+')

### QUOTES
def find_quotes(span=2):
    'query Quotes.net API, pickle matches with 2+ Q codimensions'

    try:
        i, o = pickle.load(open('_io.pkl', 'rb')) # load batch span
    except FileNotFoundError:
        i, o = (0, 1)
        pickle.dump((i, o), open('_io.pkl', 'wb'))

    try:
        batch = pickle.load(open('quotes.pkl', 'rb')) # load quote dict
    except FileNotFoundError:
        batch = {}
        pickle.dump(batch, open('quotes.pkl', 'wb'))

    dims = list(dimension_dict(thingify(Quadranym)).items())
    print(f'{len(batch)} Quotes in db. Searching {i}:{o} from {len(dims)} Q-dimensions')

    for word, quads in dims[i:o]:
        result = requests.get(f'{QUOTES_API}{word}').json()
        if 'error' in result:
            print(result['error'])
            break
        if not 'result' in result:
            continue

        for data in result['result']:
            if 'quote' not in data or isinstance(data, str):
                continue

            for quad in quads:
                if sum(quad.freq(data['quote'])) > 1:
                    qode, subs = quad.enqode(data['quote'], flag=True)
                    if len(set(subs)) > 1: # 2+ unique dimensions!
                        batch[qode] = dict(body=data['quote'],
                                           qode=qode,
                                           quadranym=quad.pk,
                                           src=data.get('author', ''),
                                           subs=subs,
                                           width=len(subs))

    pickle.dump((o, o+span), open('_io.pkl', 'wb'))
    pickle.dump(batch, open('quotes.pkl', 'wb'))
    print(f'{len(batch)} Quotes now!')

def add_quotes():
    'add quotes from pickle'

    qodes = [x.qode for x in Quote.objects.all()] # all quotes qode in db
    print(f'{len(qodes)} Quotes in nymbase')

    batch = pickle.load(open('quotes.pkl', 'rb')) # quotes dict keyed by qode
    print(f'Trying {len(batch)} quotes..')

    for item in batch.values(): # add batch to Nymbase
        if item['qode'] not in qodes and len(item['body']) < 281:
            try:
                pk = item.pop('quadranym')
                quote = Quote(**item)
                quote.quadranym = Quadranym.objects.get(pk=pk)
                quote.save()
            except DataError:
                print('DataError:', quote)

    print(f'Added {Quote.objects.count() - len(qodes)} quotes')

### FORTUNES
def add_fortunes():
    'add fortunes from datafile to nymbase'

    fortunes = open('data/fortunes.dat', 'r', encoding='utf-8').read().split('\n%\n')
    for fortune in fortunes:
        fort = Fortune(body=SPACE.sub(' ', fortune.replace('\n', ' ')).strip())
        fort.save()

def mine_fortunes():
    'mine fortunes in nymbase for quadrant-matches q1=1 or q2=2+'

    forts = Fortune.objects.all()
    quads = Quadranym.objects.all()

    for fort in forts:
        fort.q2.clear()
        fort.q1.clear()

        for quad in quads:
            got = sum(quad.freq(fort.body, ('if', 'in', 'is', 'out', 'to', 'for', 'from',
                                            'how', 'what', 'where', 'who', 'why', 'with')))
            if got > 1:
                fort.q2.add(quad)
                fort.save()
            elif got == 1:
                fort.q1.add(quad)
                fort.save()

    forts = Fortune.objects.all() # new data
    for fort in forts:
        fort.enqode_fortune()
