#!/usr/bin/env python
# encoding: utf-8
"""
utils.py -- Nymology PRE-PROCESSING tools
DATABASE: Import Django table data from:
  - nymbase.pkl -- old qControl app data
  - fortunes.dat -- 3k quotes & fortunes; thanks to bmc@clapper.org
                                    https://github.com/bmc/fortunes
ANALYSIS: Find dead urls to fix
PLOTTING: Plot Polynym distribution [deprecated]
CRAWL: Phrases.net

CODE CHECK:
pylint --load-plugins pylint_django spin/views.py > lint.txt

LOCAL QUOTE CRAWL:
dj> from utils import *
dj> mine_quotes(100) # rate limit = 100/day
dj> add_quotes()
..wait 24 hours..

REVERT TO LEGACY DATA:
>  bash wipe.sh
>  bash revert.sh
dj> from utils import *
dj> nymbase()
>  py manage.py migrate
dj> dj_nymbase()
dj> dj_fortune() # --> then mine_fortunes()
manually add P: ~fmk, mood/Ekman6, moodset/ etc.
         add Q: -, ~Topic~, qode
         add Phrase: -
         add users: davekud,kemp,lori,Greggo

IMPORT NYMOLOGY.org DATA >> LOCAL:
>  bash wipe.sh
HOST>  python3.7 manage.py dumpdata --exclude=contenttypes --exclude=auth.Permission --exclude=admin.logentry > dump.json
>  scp scotty@web615.webfaction.com:/home/scotty/webapps/dj/nym/dump.json .
>  py manage.py makemigrations
>  py manage.py migrate --run-syncdb
>  open json and delete all admin.logentry entries!
>  py manage.py loaddata dump.json

 ___________________________________________________________
             pos_dict{ word_list[ nymdict{} ] }
|___Expressions___| Poly |____________Quadranyms____________|
e_nouns, e_ztopics, nyms, noung, nouns, verbg, verbs, ztopics

"""
import re
import pickle
import requests
import subprocess
from random import choice
from json import JSONDecodeError
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

# NYMOLOGY CLASSES & METHODS
from spin.models import Polynym, Polymap, Polyset, Quadranym, Quadraset, \
                    Fable, Phrase, Story, Storyline, Tale, Taleline, \
                    Fortune, Quote, Vectornym, Winner, \
                    QN, enqodes, thingify, dimension_dict

Q = re.compile(r'q(T|E|R|O|S)') # legacy qT
QT = re.compile(r'(?i)q(\d)*?(T|E|R|O|S)') # legacy q1T
SPACE = re.compile(r'(?s)\s\s+')

# QUOTES/PHRASES API: stands4.com dashboard: hbX2yoqD
API = f'https://www.stands4.com/services/v2/quotes.php?uid=7528&tokenid=0O9HSQuPUVTHvOmP&searchtype=SEARCH&format=json&query='

### PROCESS #####################################################################
def update_users():
    'update field: x.by (string) -> x.user (foreign key)'

    u = get_user_model().objects.get(username='scotty')
    for obj in (Fable, Phrase, Polynym, Polymap, Polyset, Quadranym, Quadraset, Story, Tale, Vectornym, Winner):
        for o in obj.objects.all():
            try:
                nu = get_user_model().objects.get(username=o.by)
            except:
                nu = u
                print (o.by)
            o.user = nu
            o.save()

def qfix(txt, number=1):
    'update old qT and q1T qode to new q1n format'

    matches = list(QT.finditer(txt))
    matches.reverse() # start at end
    for m in matches:
        n = m.group(1) # txt number overrides input
        q = m.group(2).lower() # dimension(t,e,r,o,s)
        q = q if q != 't' else 'n' # update t/T(opic) to n(ame)
        txt = f'{txt[:m.start()]}q{number if not n else n}{q}{txt[m.end():]}'
    return txt

def urlfix():
    'best try at http nonsense'

    for obj in (Polynym, Polymap, Quadranym, Phrase):
        for it in obj.objects.all():
            url = it.url
            if not url: continue
            if url.startswith('http://https://'):
                it.url = url.replace('http://https://', 'http://')
                it.save()
            elif not url.startswith('http://') and not url.startswith('https://'):
                it.url = 'http://'+url
                it.save()

def emptyfix():
    'set .  to "" (blank=True)'

    nyms = Quadranym.objects.all()
    for nym in nyms:
        for atr in ('by', 'src', 'url', 'area', 'pos', 'e', 'r', 'o', 's', 'epos', 'rpos', 'opos', 'spos', 'realm'):
            if getattr(nym, atr) == '.':
                setattr(nym, atr, '')
                nym.save()
                print(f'[{nym.name}] {atr}: clear')

    nyms = Polynym.objects.all()
    for nym in nyms:
        for atr in ('by', 'src', 'url', 'area', 'mode', 'p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8', 'p9', 'p10', 'p11', 'p12'):
            if getattr(nym, atr) == '.':
                setattr(nym, atr, '')
                nym.save()
                print(f'[{nym.name}] {atr}: clear')

### IMPORT #####################################################################
def nymbase():
    '''copy/reload DB, add POS/Z, toss date, fix fields:
            t/title=>name
            author=>by
            source=>src
            used=>mode
            poly=>p'''

    subprocess.run("rm -f db.sqlite3", shell=True, check=True)
    subprocess.run("rm -f data/nymbase.pkl", shell=True, check=True)
    subprocess.run("cp data/nymbase_bk.pkl data/nymbase.pkl", shell=True, check=True)
    base = pickle.load(open('data/nymbase.pkl', 'rb'))
    nuDB = {}

    for nym in base.keys():
        nu = []
        pos = None
        if nym in ('noung','nouns'):     # POS use WordNet tags:
            pos = 'NN'                   #  https://bit.ly/2QTI752
        elif nym in ('verbg','verbs'):
            pos = 'VB'
        z = None
        if nym in ('nouns','verbs'):     # Z-TOPIC
            z = 0
        elif nym in ('ztopics','e_ztopics','verbg','noung'):
            z = 1

        for this in base[nym]:
            if z is not None:                   # z
                this['z'] = z
            if pos is not None:                 # POS
                this['pos'] = pos
            if 'title' in this:                 # name
                this['name'] = this.pop('title')
            elif 't' in this:
                this['name'] = this.pop('t')
            if 'source' in this:                # src
                this['src'] = this.pop('source')
            if 'author' in this:                # by
                this['by'] = this.pop('author')
            if 'poly' in this:                  # p > depth
                this['depth'] = this.pop('poly')
            if 'used' in this:                  # mode
                this['mode'] = this.pop('used')
            if 'date' in this:                  # date
                del this['date']     # <<!TOSS DATA!<<
            if nym in ('e_nouns','e_ztopics'):   # subs/depth
                this['qode'] = qfix(this.pop('body'))
                subs = [x.group(2) for x in QN.finditer(this['qode'])]
                this['subs'] = ''.join(subs).upper()
                this['width'] = len(subs) # here, depth == len(subs)
            elif nym == 'nyms':                  # p1,p2..
                segs = this.pop('body').split(',')
                for i,seg in enumerate(segs):
                    i += 1
                    this['p%i' % i] = seg
            nu.append(this)
        nuDB[nym] = nu
    pickle.dump(nuDB, open('data/nymbase.pkl', 'wb'))

def dj_nymbase():
    'add all Nymbase => django: Polynym, Quadranym,Phrase'

    base = pickle.load(open('data/nymbase.pkl', 'rb'))
    for nym in ('nouns','noung','verbs','verbg','ztopics','nyms','e_nouns','e_ztopics'):
        db = base[nym]
        print ('\ndB[%s]' % nym)

        if nym in ('nouns', 'noung','verbs','verbg','ztopics'):
            for this in db:
                print ('nym[%s]' % this.get('name', 'UNKNOWN'))
                q = Quadranym(**this)
                q.save()
        elif nym in ('e_nouns','e_ztopics'):
            for this in db:
                print ('nym[%s]' % this['name'])
                t = Phrase(**this)
                t.save()
        else:
            for this in db:
                print ('nym[%s]' % this['name'])
                p = Polynym(**this)
                p.save()

def dj_fortune():
    'add fortunes to db'

    fortunes = open('data/fortunes.dat', 'r', encoding='utf-8').read().split('\n%\n')
    for fortune in fortunes:
        f = Fortune(body=SPACE.sub(' ', fortune.replace('\n',' ')).strip())
        f.save()

### MINE #######################################################################
def mine_fortunes():
    'mine fortunes for quadrant-matches q1=1 or q2=2+'

    forts = Fortune.objects.all()
    quads = Quadranym.objects.all()
    for fort in forts:
        fort.q2.clear()
        fort.q1.clear()
        for quad in quads:
            got = sum(quad.freq(fort.body, ('if','in','is','out','to','for','from','how','what','where','who','why','with')))#stopwords
            if got > 1:
                fort.q2.add(quad)
                fort.save()
            elif got == 1:
                fort.q1.add(quad)
                fort.save()
    forts = Fortune.objects.all() # new data
    for fort in forts:
        fort.enqode_fortune()

def mine_quotes(span=2):
    'query Quotes.net API, pickle matches with 2+ Q codimensions'

    try:
        i,o = pickle.load(open('_io.pkl', 'rb')) # load batch span
    except FileNotFoundError:
        pickle.dump((0, 1), open('_io.pkl','wb'))

    try:
        batch = pickle.load(open('quotes.pkl', 'rb')) # load quote dict
    except FileNotFoundError:
        pickle.dump({}, open('quotes.pkl','wb'))

    dims = list(dimension_dict(thingify(Quadranym)).items())
    print(f'{len(batch)} Quotes! {len(dims)} Q-dimensions! Slicing {i}:{o}')

    for word, quads in dims[i:o]:
        result = requests.get(f'{API}{word}').json()
        if 'error' in result:
            print(result['error'])
            break
        elif not 'result' in result:
            print('Result:',result)
            continue
        for data in result['result']:
            if 'quote' not in data or isinstance(data, str):
                print('Data:',data)
                continue
            for quad in quads:
                if sum(quad.freq(data['quote'])) > 1:
                    qode, subs = quad.enqode(data['quote'], flag=True)
                    if len(set(subs)) > 1: # 2+ unique dimensions!
                        src = data.get('author', '')
                        if src != 'Musin Almat Zhumabekovich':
                            batch[qode] = dict(body=data['quote'],
                                          qode=qode,
                                          quadranym=quad.pk,
                                          src=src,
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

    for bat in batch.values(): # add batch to Nymbase
        if bat['qode'] not in qodes:
            pk = bat.pop('quadranym')
            quote = Quote(**bat)
            quote.quadranym = Quadranym.objects.get(pk=pk)
            quote.save()
            print(quote)

    print(f'Added {Quote.objects.count() - len(qodes)} quotes')

### CRAWL ######################################################################
def add_wikis():
    'run wikipedia search on objects w/o urls'

    for obj in (Polynym, Quadranym):
        did = 0
        for it in obj.objects.all():
            did += it.add_wiki()
        print(f'{str(obj)[20:-2]}: += {did} URLs\n__')

### ANALYZE ####################################################################
def dead_urls():
    'find dead URLs'

    from webutils import link
    urls = {}
    for obj in (Polynym,Quadranym):
        objs = obj.objects.all()
        urls[obj.__name__] = [(x.name, x.url) for x in objs if x.url and link(x.url) is None]
    return urls

################################################################################
### RUN
if __name__ == '__main__':
    mine_quotes()
