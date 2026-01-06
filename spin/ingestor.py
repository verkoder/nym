#!/usr/bin/env python
# encoding: utf-8
'''
ingestor.py -- Nymology API data ingestor
'''
import json
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.db import IntegrityError
from django.db.utils import OperationalError
from .models import COMMON, UNCOMMON, get_user_model, Guessanym, Polynym

INGEST_ORDER = ( # {model: API endpoint}
    'fable',
    'phrase',
    'polynym',
    'polymap', # Polynym req
    'polyset', # [Polynym] req
    'quadranym',
    'quadraset', # [Quadranym] req
    'queue',
    'story',
    'tale', # Fable req
    'vectornym', # Polynym req
    'storyline', # Story/Phrase/Quadranym req
    'taleline', # Tale/Quadranym req
    'fortune', # [Quadranym] req
    'quote', # Quadranym req
    'winner' # User req
)
USERNAMES = ('dane', 'davekud', 'Greggo', 'kemp', 'lori') # OG's +scotty/superuser
DATA = {**COMMON, **UNCOMMON}
FOREIGN = { # {foreign/m2m field: linked class}
    'fable': 'fable',
    'pa': 'polynym', # polymap
    'pb': 'polynym',
    'phrase': 'phrase',
    'quadranym': 'quadranym',
    'q1': 'quadranym', # fortune
    'q2': 'quadranym',
    'story': 'story',
    'tale': 'tale',
    'v1': 'polynym', # vectornym
    'v2': 'polynym',
    'v3': 'polynym',
    'v4': 'polynym',
    'v5': 'polynym',
    'v6': 'polynym',
    'v7': 'polynym',
    'v8': 'polynym',
    'v9': 'polynym',
}
FOREIGN_KEYS = FOREIGN.keys()
UNIQUE = { # {model: unique fields for keyless data retrieval}
    'fable': ('qode',),
    'phrase': ('qode',),
    'polynym': ('name', 'depth', 'src', 'area', 'wiki', 'p1', 'p2', 'p3',
                'p4', 'p5', 'p6', 'p7', 'p8', 'p9', 'p10', 'p11', 'p12'),
    'quadranym': ('name', 'e', 'r', 'o', 's', 'pos'),
    'story': ('name',),
    'tale': ('name',),
}

def dump_wikis():
    'STEP 1a: save Polynym wikipedia name/URLs to json [NEXT STEP 2: scrapy crawl] NEED unused node-wikis'
    urls = {w: n for w,n in Polynym.data.values_list('wiki', 'name')}
    urls = [{'wiki': k, 'name': v} for k,v in urls.items()]
    json.dump(urls, open('./data/polywikis.json', 'w'))

def dump_nodes():
    'STEP 1b: save Polynym node wikipedia URLs to json [NEXT STEP 2: scrapy crawl] NEED unused node-wikis'
    nodes = set()
    for p in Polynym.data.all():
        nodes.update(p.names())
    nodes = [{'word': x} for x in nodes]
    json.dump(nodes, open('./data/polynodes.json', 'w'))

def make_guessanyms():
    'STEP 3: load scraped data, create Guessanyms [STEP 4: human cycles on /guessanyms] UPLOAD JSON TO SERVER!'
    guess = json.load(open('./data/polyguess.json')) # LOCAL
    #guess = json.load(open('../data/polyguess.json')) # SERVER
    for g in guess:
        try:
            gnym = Guessanym(
                name=g['name'],
                depth=g['depth'],
                paragraph=g['paragraph'],
                sentence=g['sentence'],
                wiki=g['wiki'],
                word=g['word'],
                p1=g.get('p1', '').strip(),
                p2=g.get('p2', '').strip(),
                p3=g.get('p3', '').strip(),
                p4=g.get('p4', '').strip(),
                p5=g.get('p5', '').strip(),
                p6=g.get('p6', '').strip(),
                p7=g.get('p7', '').strip(),
                p8=g.get('p8', '').strip(),
                p9=g.get('p9', '').strip(),
                p10=g.get('p10', '').strip(),
                p11=g.get('p11', '').strip(),
                p12=g.get('p12', '').strip()
            )
            gnym.save()
        except IntegrityError: # non unique
            pass
        except OperationalError as e:
            print(e)

def add_users():
    'add original users'
    for username in USERNAMES:
        user = get_user_model()(username=username)
        try:
            user.save()
        except IntegrityError:
            pass#print(f'We know {username}!')

def get_user(username):
    return get_user_model().objects.get(username=username)

def ingest(dataset, data):
    'download NymologyAPI data, add to local db'
    print(f'Ingesting {len(data)} {dataset.title()}s..')
    was = {'added': 0, 'skipped': 0, 'errors': []}
    for entry in data:
        thing = DATA[dataset]()
        polys = False if 'polynyms' not in entry else entry.pop('polynyms') # hold m2m field data..
        quads = False if 'quadranyms' not in entry else entry.pop('quadranyms')
        q1 = False if 'q1' not in entry else entry.pop('q1')
        q2 = False if 'q2' not in entry else entry.pop('q2')
        q2 = False if 'q2' not in entry else entry.pop('q2')
        voters = False if 'voters' not in entry else entry.pop('voters') # hold voters list..
        for field, value in entry.items():
            if field.endswith('_id'):
                continue
            if value and field in FOREIGN_KEYS:
                value, err = seek(FOREIGN[field], value)
                if not value:
                    was['errors'].extend(err+[f'No seek {field}: {entry}'])
                    continue
                setattr(thing, field, value)
                was['errors'].extend(err)
            elif field == 'user':
                thing.user = get_user(value)
            elif field == 'voters':
                for usr in value:
                    thing.votes.up(get_user(usr).pk)
            elif field != 'likes': # computed by VoteModel
                setattr(thing, field, value) # actual field!
        try:
            thing.save()
        except IntegrityError:
            print(f'Skipped dupe: {thing}')
            was['skipped'] += 1
            continue
        if polys: # ..finally add m2m fields..
            polys,err = seek('polynym', polys, many=True)
            thing.polynyms.set(polys)
            was['errors'].extend(err)
        if quads:
            quads,err = seek('quadranym', quads, many=True)
            thing.quadranyms.set(quads)
            was['errors'].extend(err)
        if q1:
            q1,err = seek('quadranym', q1, many=True)
            thing.q1.set(q1)
            was['errors'].extend(err)
        if q2:
            q2,err = seek('quadranym', q2, many=True)
            thing.q2.set(q2)
            was['errors'].extend(err)
        if voters: # ..finally add voters..
            for voter in voters:
                thing.votes.up(get_user(voter).pk)
        was['added'] += 1
    print(f'--->> {dataset.upper()} INGESTION >>-- {was}\n')

def seek(dataset, thing_data, many=False):
    'find thing(s) from model and unique data'
    if not thing_data:
        return thing_data
    out = []
    err = []
    if not many:
        thing_data = {k:v for k,v in thing_data.items() if v and k in UNIQUE[dataset]}
        try:
            out = DATA[dataset].objects.get(**thing_data)
        except MultipleObjectsReturned:
            out = DATA[dataset].objects.filter(**thing_data)
            err = [f'NOT UNIQUE: {len(out)} {dataset}s @ {thing_data}']
            out = out[0]
        except ObjectDoesNotExist:
            err = [f'DOES NOT EXIST: {dataset} @ {thing_data}']
        return out, err
    for this_data in thing_data:
        got, nope = seek(dataset, this_data) # recursion
        if got:
            out.append(got)
        if nope:
            err.extend(nope)
    return out, err

def mass_ingest(api, saved=False):
    'download & ingest all NymologyAPI data; saved=True to use saved JSON'
    add_users()
    for dataset in INGEST_ORDER:
        ingest(dataset, api.get_data(dataset) if not saved else api.get_file(dataset))
