'''
do_conceptnet.py -- ConceptNet NLP tools
'''
from time import sleep
from json import JSONDecodeError
from itertools import combinations
from functools import wraps
import requests

API = 'http://api.conceptnet.io/'
EN = '?filter=/c/en'
RELS = (# CN relations
    'RelatedTo',
    'FormOf',
    'IsA',
    'PartOf',
    'HasA',
    'UsedFor',
    'CapableOf',
    'AtLocation',
    'Causes',
    'HasSubevent',
    'HasFirstSubevent',
    'HasLastSubevent',
    'HasPrerequisite',
    'HasProperty',
    'MotivatedByGoal',
    'ObstructedBy',
    'Desires',
    'CreatedBy',
    'Synonym',
    'Antonym',
    'DistinctFrom',
    'DerivedFrom',
    'SymbolOf',
    'DefinedAs',
    'MannerOf',
    'LocatedNear',
    'HasContext',
    'SimilarTo',
    'EtymologicallyRelatedTo',
    'EtymologicallyDerivedFrom',
    'CausesDesire',
    'MadeOf',
    'ReceivesAction',
    'ExternalURL'
)
EKMAN6 = ('sad', 'happy', 'angry', 'disgusted', 'surprised', 'afraid')
QSET = {
    'prime': dict(e=['expansion'], r=['reduction'], o=['objective'], s=['subjective']),
    'ez': dict(e=['more'], r=['less'], o=['goal'], s=['self']),
    'nice': dict(e=['more', 'open', 'expand'], r=['less', 'close', 'reduce'], o=['goal', 'object', 'subjective'], s=['self', 'subject', 'subjective'])
}

### DECORATORS:
def cn(meth):
    'let methods take free text / websafe input'

    @wraps(meth)
    def cn_meth(*args, **kwargs):
        args = [x.replace(' ', '_') for x in args if x]
        kwargs = {k:x.replace(' ', '_') for k, x in kwargs.items() if x}
        return meth(*args, **kwargs)
    return cn_meth

### METHODS
def sims(li):
    'compare concepts list'

    for a, b in combinations(li):
        print(f'{a}::{b}={sim(a,b)}')

def focus(topics, goals):
    'hone varied topics towards a synset of concept goals'

    hone = {}
    hits = 0
    #when = time()
    for top in topics:
        ties = 0
        for gol in goals:
            ties += sim(top, gol)
            hits += 1
            sleep(2)
        hone[top] = ties
    #when = time() - when
    #print (f'{hits} API hits in {when:.2f} ~> avg = {hits/when:.2f}')
    return sorted(hone.items(), key=lambda x: x[1], reverse=True)

def guess_quadranym(topic, qset):
    'guess quadranym dimensions from a topic'

    eros = {}
    q = QSET['prime'] if not qset else QSET[qset]
    topics = related(topic)
    for quadrant, dimensions in q.items():
        eros[quadrant] = focus(topics, dimensions)[:12]
    return eros

def guess_mood(topic, moods=EKMAN6):
    'guess mood of a topic from moods / mood synsets (or nyms /nym-synset)'

    feel = {}
    for mood in moods:
        ro = 0
        sco = 0
        syns = mood.split(',')
        for syn in syns:
            emo = sim(topic, syn)
            if emo:
                sco += emo
                ro += 1
        if sco:
            feel[syns[0]] = emo * 100 / ro
    return sorted(feel.items(), key=lambda x: x[1], reverse=True)

def guess_fit(topics, nyms):
    'assign best topic-per-nym'

    # collect master fit list, by pair
    fits = []
    for nym in nyms:
        fits.extend([((nym, t), v) for t, v in guess_mood(nym, topics)])
    fits.sort(key=lambda x: x[1])

    # top fit-per-topic til nyms are matched
    nymli = list(nyms)
    best = {t:('', 0) for t in topics}
    while nyms and fits:
        (nym, top), sco = fits.pop()
        if nym in nymli and (sco > best[top][1] or best[top][1] == 0):
            nymli.remove(nym)
            best[top] = nym, sco

    # order by nym
    best = {v[0]:(k, v[1]) for k, v in best.items()}
    return [x for x in [best.get(nym) for nym in nyms] if x]

### API METHODS
@cn
def query(a, b=None):
    'edges containing input(s); "node" lookup'

    if b is None:
        js = requests.get(f'{API}query?node=/c/en/{a}{EN}').json()
    js = requests.get(f'{API}query?node=/c/en/{a}&other=/c/en/{b}').json()
    return [x['@id'][6:].replace('_', ' ') for x in js['related']]

@cn
def related(a):
    'close concepts to input; "related" terms'

    js = requests.get(f'{API}related/c/en/{a}{EN}').json()
    return [x['@id'][6:].replace('_', ' ') for x in js['related'] if x not in (a, f'{a}s')]

@cn
def corelated(a, b):
    'return overlapping related terms if any'

    a_terms = set(related(a))
    b_terms = set(related(b))
    return list(a_terms.intersection(b_terms))

@cn
def sim(a, b=None):
    'a:b concept similarity; "relatedness" value 0-1'

    if not a or not b:
        return 0.0
    try:
        js = requests.get(f'{API}relatedness?node1=/c/en/{a}&node2=/c/en/{b}').json()
    except JSONDecodeError:
        return 0.0
    return abs(js['value'])
