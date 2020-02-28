"""
models.py -- Nymology Django classes

Nymology by G.S Vercoe & D.C Scalise
Copyright (c) 2009-9999 Nymoholics Unlimited.
"""
import re
from time import time
from random import choice, sample
from itertools import combinations
import urllib3

from django.db import models
from django.urls import reverse
#from django.shortcuts import redirect, render
from django.db.models.functions import Lower
from django.contrib.auth import get_user_model
from vote.models import VoteModel

#####>>> SPACY NLP ON/OFF SWITCH <<<#####
from .do_spacy import eat,retoke,inflect
NLP = True
#NLP = False

# qode regx groups 1=qid 2=quadrant _/^  3=postag
QN = re.compile(r'q(\d+)(n|e|r|o|s)_?\^?([A-Z]+)?', re.I) # q1n_POS format
NEWLINE = re.compile(r'[\n\r]+')
NEWLINE2 = re.compile(r'[\n\r]{3,}')
TAGS = re.compile(r'</?[A-Za-z]+>')

# WEB CRAWLER
HTTP = urllib3.PoolManager()

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

####################
### DB SHORTCUTS ###
def thingify(obj):
    'objects from any Common'

    if obj is Polynym:
        return Polynym.objects.exclude(name__in=['~fmk', 'moodset'])

    if obj is Quadranym:
        return Quadranym.objects.exclude(name__in=['-', '~Topic~'])

    if obj is Phrase:
        return Phrase.objects.exclude(name='-')

    return obj.objects.all()

def orderfy(obj=None, n=None):
    'ordered list of Common objects'

    if obj is Polynym: # omit FMK, moodsets
        if n is not None:
            return Polynym.objects.filter(depth=n) \
                                  .exclude(name__in=['~fmk', 'moodset']) \
                                  .order_by(Lower('name'))
        return Polynym.objects.exclude(name__in=['~fmk', 'moodset']) \
                              .order_by(Lower('name'))

    if obj is Quadranym: # omit line break, topic
        return Quadranym.objects.exclude(name__in=['-', '~Topic~']) \
                                .order_by(Lower('name'))

    if obj is Phrase: # omit line break
        return Phrase.objects.exclude(name='-').order_by(Lower('name'))

    if obj is Quote: # sort by source
        return Quote.objects.all().order_by(Lower('src'))

    if obj is Fortune: # only 2+ codimensions
        return Fortune.objects.exclude(q2=None).order_by(Lower('body'))

    if obj is Queue: # undone to-do qQ
        return sorted(list({x.name for x in Queue.objects.all()} \
                         - {x.name for x in thingify(Quadranym)}))

    if obj is None: # done to-do qQ
        return sorted(list({x.name for x in thingify(Quadranym)} \
                         & {x.name for x in Queue.objects.all()}))

    return obj.objects.all().order_by(Lower('name'))

###########################
### NYMOLOGY ROOT CLASS ###
class Common(VoteModel, models.Model):
    'Common Nymology root class'

    name = models.CharField(max_length=128) # COMMON FIELDS
    user = models.ForeignKey(get_user_model(), on_delete=models.DO_NOTHING, blank=True, null=True)
    src = models.CharField(max_length=128, blank=True, verbose_name='source')
    area = models.CharField(max_length=32, blank=True)
    wiki = models.CharField(max_length=128, blank=True, verbose_name='info link')

    class Meta:
        abstract = True
        ordering = ['name']

    def named(self):
        'string-escaped name'

        return self.name.replace(' ', '\ ')

    def whois(self):
        'which object name'

        return self.__class__.__name__.lower()

    def get_absolute_url(self, *args, **kwargs):
        return reverse(f'spin:{self.whois()}_detail', kwargs={'pk': self.pk})

######################
### COMMON CLASSES ###
class Polynym(Common):
    'Polynym class: idea set/multi-term system up to depth 12; use comma-separated lists for synonym sets'

    mode = models.CharField(max_length=8, blank=True)
    depth = models.PositiveSmallIntegerField()
    p1 = models.CharField(max_length=128)
    p2 = models.CharField(max_length=128)
    p3 = models.CharField(max_length=128, blank=True)
    p4 = models.CharField(max_length=128, blank=True)
    p5 = models.CharField(max_length=128, blank=True)
    p6 = models.CharField(max_length=128, blank=True)
    p7 = models.CharField(max_length=128, blank=True)
    p8 = models.CharField(max_length=128, blank=True)
    p9 = models.CharField(max_length=128, blank=True)
    p10 = models.CharField(max_length=108, blank=True)
    p11 = models.CharField(max_length=128, blank=True)
    p12 = models.CharField(max_length=128, blank=True)

    def nyms(self, named=False):
        'all nyms; named=True includes Polynym name'

        if not named:
            return [x for x in [self.p1, self.p2, self.p3, self.p4, self.p5, self.p6,
                                self.p7, self.p8, self.p9, self.p10, self.p11, self.p12] if x]
        return [x for x in [self.name, self.p1, self.p2, self.p3, self.p4, self.p5, self.p6,
                            self.p7, self.p8, self.p9, self.p10, self.p11, self.p12] if x]

    def pairs(self, named=True):
        'all possible nym pairs'

        return list(combinations(self.nyms(named=named), 2))

    def triangles(self, named=True):
        'all possible triangles'

        return list(combinations(self.nyms(named=named), 3))

    def quadrangles(self, named=True):
        'all possible quadrangles'

        return list(combinations(self.nyms(named=named), 4))

    def __str__(self):
        return f'<P{self.depth}:{self.name}|{self.mode}|{self.area}|{self.user}|{self.src}>'

class Quadranym(Common):
    'Quadranym class: sensibility model node'

    e = models.CharField(max_length=128, verbose_name='expansion')
    r = models.CharField(max_length=128, verbose_name='reduction')
    o = models.CharField(max_length=128, verbose_name='objective')
    s = models.CharField(max_length=128, verbose_name='subjective')
    pos = models.CharField(max_length=8, blank=True, verbose_name='POS')
    epos = models.CharField(max_length=8, blank=True, verbose_name='/e')
    rpos = models.CharField(max_length=8, blank=True, verbose_name='/r')
    opos = models.CharField(max_length=8, blank=True, verbose_name='/o')
    spos = models.CharField(max_length=8, blank=True, verbose_name='/s')
    realm = models.CharField(max_length=32, blank=True)

    def enqode(self, text, number=1, flag=False):
        'POS-sensitive Q-notation encoder: input text, optional number; flag returns count'

        dims = {self.name:'n', self.e:'e', self.r:'r', self.o:'o', self.s:'s'}
        words = [(x.text, x.lemma_, x.tag_) for x in eat(text)]
        neros = []
        out = []

        for word, lem, tag in words:
            if word in dims:
                neros.append(dims[word])
                word = f'q{number}{dims[word]}_{tag}'
            elif lem in dims:
                neros.append(dims[lem])
                word = f'q{number}{dims[lem]}_{tag}' # POS change!
            out.append(word)
        out = retoke(out).text.replace(" ’", "’").replace(" n’", "n’") # <~ BETTER RETOKE?!

        return out if not flag else out, ''.join(neros).upper()

    def deqode(self, text, number=1, nlp=NLP, trace=False):
        'POS-sensitive Q-notation decoder (regex): input text, optional number; nlp=False to disable spaCy/inflect'

        matches = list(QN.finditer(text))
        subs = []
        slide = 0

        # qode slide
        for m in matches:
            if int(m.group(1)) == number: # Q index only
                quadrant = m.group(2)
                nu = getattr(self, quadrant if quadrant != 'n' else 'name')
                nu = nu.capitalize() if m.start() == 0 or m.group(0)[0].isupper() else nu
                nu = nu if not trace or nlp else f'<b>{nu}</b>' # only trace w/o nlp
                i = m.start() - slide
                o = m.end() - slide
                text = f'{text[:i]}{nu}{text[o:]}'
                diff = len(m.group(0)) - len(nu)
                slide += diff
                o -= diff
                subs.append((i, o, nu, m.group(3))) # (in, out, new-uninflected, new-pos)

        # conjugal slide
        if nlp:
            slide = 0
            doc = eat(text)
            for i, o, un, pos in subs:
                flect = inflect(doc, un, pos) # inflect to new-pos
                flect = un if not flect else flect
                flect = flect if not un[0].isupper() else flect.capitalize()
                flect = flect if not trace else f'<b>{flect}</b>' # nlp trace
                i -= slide
                o -= slide
                text = f'{text[:i]}{flect}{text[o:]}'
                slide += len(un) - len(flect)

        return text.replace(" '", "'")

    def freq(self, text, omit=None):
        'mine text for current topic/quadrants, return Q-freq NEROS-tuple'

        text = [x for x in text.split() if not x in omit] if omit is not None else text.split()
        return [text.count(x) for x in [self.name, self.e, self.r, self.o, self.s]]

    def nyms(self, named=True):
        'all nyms; named=True includes Quadranym name'

        if not named:
            return [x for x in [self.e, self.r, self.o, self.s] if x]
        return [x for x in [self.name, self.e, self.r, self.o, self.s] if x]

    def pairs(self, named=True):
        'all possible nym pairs'

        return list(combinations(self.nyms(named=named), 2))

    def triangles(self, named=True):
        'all possible triangles'

        return list(combinations(self.nyms(named=named), 3))

    def quadrangles(self, named=True):
        'all possible quadrangles'

        return list(combinations(self.nyms(named=named), 4))

    def __str__(self):
        return f'<Q:{self.name}|{self.pos}|{self.area}|{self.user}|{self.src}>'

class Phrase(Common):
    'Phrase class: enqoded phrasal template (single-topic)'

    qode = models.CharField(max_length=2048)
    subs = models.CharField(max_length=32, blank=True)
    width = models.PositiveSmallIntegerField(default=0)
    realm = models.CharField(max_length=32, blank=True)

    def spin(self, quadranym, trace=False):
        'spin Phrase with input Quadranym'

        return quadranym.deqode(self.qode, trace=trace)

    def nyms(self):
        'all words in Phrase'

        return [x.replace(',', '').replace('.', '') for x in self.qode.split()]

    def __str__(self):
        return f'<Ph{self.width}:{self.name}|{self.area}|{self.user}|{self.src}>'

class Fable(Common):
    'Fable class: enqoded phrasal template (multi-topic)'

    qode = models.CharField(max_length=4096)
    subs = models.CharField(max_length=32, blank=True)
    length = models.PositiveSmallIntegerField(default=0)
    width = models.PositiveSmallIntegerField(default=0)
    realm = models.CharField(max_length=32, blank=True)

    def spin(self, quadranyms, trace=False):
        'spin Fable with Quadranym list'

        return deqodes(quadranyms, self.qode, trace=trace)

    def nyms(self):
        'all words in Fable'

        return [x.replace(',', '').replace('.', '') for x in self.qode.split()]

    def __str__(self):
        return f'<F{self.length}x{self.width}:{self.name}|{self.area}|{self.user}|{self.src}>'

class Tale(Common):
    'Tale class: user-spun Fable; builds Taleline data'

    length = models.PositiveSmallIntegerField(default=0)
    fable = models.ForeignKey(Fable, related_name="fable", on_delete=models.CASCADE)

    def quads(self):
        'associated Taleline Quadranym list'

        return [q.quadranym for q in Taleline.objects.filter(tale=self.pk)]

    def tell(self):
        'tell Tale by its Fable and Taleline Quadranym list'

        return deqodes(self.quads(), self.fable.qode)

    def tell_trace(self):
        'tell Tale by its Fable and Taleline Quadranym list -- with trace'

        return deqodes(self.quads(), self.fable.qode, trace=True)

    def __str__(self):
        return f'<T{self.length}:{self.name}|{self.area}|{self.user}|{self.src}>'


class Story(Common):
    'Story class: user-spun Phrase/Quadranym list; builds Storyline data'

    length = models.PositiveSmallIntegerField(default=0)
    realm = models.CharField(max_length=32, blank=True)

    def pairs(self):
        'Phrase, Quadranym lists from related Storyline'

        quads = [q.quadranym for q in Storyline.objects.filter(story=self.pk)]
        phras = [q.phrase for q in Storyline.objects.filter(story=self.pk)]
        if len(phras) != len(quads):
            return [], []

        return phras, quads

    def tell(self):
        'tell Story by its Storyline Phrase and Quadranym lists'

        return pairspin(*self.pairs())

    def tell_trace(self):
        'tell Story by its Storyline Phrase and Quadranym lists -- with trace'

        return pairspin(*self.pairs(), trace=True)

    def __str__(self):
        return f'<S{self.length}:{self.name}|{self.area}|{self.user}|{self.src}>'

class Vectornym(Common):
    'Vectornym class: Polynym vector'

    length = models.PositiveSmallIntegerField(default=0) # UNIQUE FIELDS
    width = models.PositiveSmallIntegerField(default=0)
    depth = models.PositiveSmallIntegerField(default=0)
    realm = models.CharField(max_length=32, blank=True)
    v1 = models.ForeignKey(Polynym, related_name="pnym_1", on_delete=models.CASCADE)
    v2 = models.ForeignKey(Polynym, related_name="pnym_2", on_delete=models.CASCADE)
    v3 = models.ForeignKey(Polynym, related_name="pnym_3", on_delete=models.CASCADE, blank=True, null=True)
    v4 = models.ForeignKey(Polynym, related_name="pnym_4", on_delete=models.CASCADE, blank=True, null=True)
    v5 = models.ForeignKey(Polynym, related_name="pnym_5", on_delete=models.CASCADE, blank=True, null=True)
    v6 = models.ForeignKey(Polynym, related_name="pnym_6", on_delete=models.CASCADE, blank=True, null=True)
    v7 = models.ForeignKey(Polynym, related_name="pnym_7", on_delete=models.CASCADE, blank=True, null=True)
    v8 = models.ForeignKey(Polynym, related_name="pnym_8", on_delete=models.CASCADE, blank=True, null=True)
    v9 = models.ForeignKey(Polynym, related_name="pnym_9", on_delete=models.CASCADE, blank=True, null=True)

    def polys(self):
        'Polynym objects'

        return [p for p in [self.v1, self.v2, self.v3, self.v4, self.v5,
                            self.v6, self.v7, self.v8, self.v9] if p]

    def names(self):
        'Polynym names'

        return [p.name for p in self.polys()]

    def nyms(self, named=False):
        'Polynym dimensions as a list of lists'

        return [p.nyms(named=named) for p in self.polys()]

    def dimensions(self, named=False):
        'Polynym dimensions as merged list'

        return [nym for nyms in [p.nyms(named=named) for p in self.polys()] for nym in nyms]

    def __str__(self):
        return f'<Pvec{self.length}x{self.width}:{self.name}|{self.area}|{self.user}|{self.src}>'

class Polymap(Common):
    'Polymap class: Polynym relationship'

    pa = models.ForeignKey(Polynym, related_name="pnym_a", on_delete=models.CASCADE) # UNIQUE FIELDS
    pb = models.ForeignKey(Polynym, related_name="pnym_b", on_delete=models.CASCADE)
    r1 = models.CharField(max_length=128)
    r2 = models.CharField(max_length=128, blank=True)
    r3 = models.CharField(max_length=128, blank=True)
    r4 = models.CharField(max_length=128, blank=True)
    r5 = models.CharField(max_length=128, blank=True)
    r6 = models.CharField(max_length=128, blank=True)
    r7 = models.CharField(max_length=128, blank=True)
    r8 = models.CharField(max_length=128, blank=True)
    r9 = models.CharField(max_length=128, blank=True)
    r10 = models.CharField(max_length=128, blank=True)
    r11 = models.CharField(max_length=128, blank=True)
    r12 = models.CharField(max_length=128, blank=True)

    def rels(self):
        'relations as list of lists'

        return [x.split(',') for x in [self.r1, self.r2, self.r3, self.r4, self.r5, self.r6, \
                                       self.r7, self.r8, self.r9, self.r10, self.r11, self.r12] if x]

    def __str__(self):
        return f'<Pmap:{self.name}|{self.area}|{self.user}|{self.src}>'

class Polyset(Common):
    'Polyset class: set of Polynyms'

    polynyms = models.ManyToManyField(Polynym)
    length = models.PositiveSmallIntegerField(default=0)
    width = models.PositiveSmallIntegerField(default=0)
    depth = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f'<Pset{self.length}x{self.width}:{self.name}|{self.area}|{self.user}|{self.src}>'

class Quadraset(Common):
    'Quadraset class: set of Quadranyms'

    quadranyms = models.ManyToManyField(Quadranym)
    length = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f'<Qset{self.length}:{self.name}|{self.area}|{self.user}|{self.src}>'

#######################
### SPECIAL CLASSES ###
class Taleline(models.Model):
    'Taleline class: Tale plot line; cascade-delete on Tale delete'

    tale = models.ForeignKey(Tale, on_delete=models.CASCADE)
    rank = models.PositiveSmallIntegerField()
    quadranym = models.ForeignKey(Quadranym, on_delete=models.CASCADE)

class Storyline(models.Model):
    'Story class: Story plot line; cascade-delete on Story delete'

    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    rank = models.PositiveSmallIntegerField()
    phrase = models.ForeignKey(Phrase, on_delete=models.CASCADE)
    quadranym = models.ForeignKey(Quadranym, on_delete=models.CASCADE)

class Queue(models.Model):
    'Queue class: Quadranyms to-do list'

    name = models.CharField(max_length=128)

    def __str__(self):
        return f'<Queue:{self.name}>'

class Quote(models.Model):
    'Quote class: enqoded Quote'

    body = models.CharField(max_length=2048)
    qode = models.CharField(max_length=2048, blank=True)
    quadranym = models.ForeignKey(Quadranym, on_delete=models.CASCADE)
    subs = models.CharField(max_length=32, blank=True)
    width = models.PositiveSmallIntegerField(default=0)
    src = models.CharField(max_length=128)

    def spin_quote(self, quadranym, trace=False):
        'spin Quote with Quadranym'

        return quadranym.deqode(self.qode, trace=trace)

    def __str__(self):
        return f'<Quote:{self.width}|{self.subs}|{self.src}>'

class Fortune(models.Model):
    'Fortune class: enqoded quotes and sayings'

    body = models.CharField(max_length=2048)
    qode = models.CharField(max_length=2048, blank=True)
    q1 = models.ManyToManyField(Quadranym)
    q2 = models.ManyToManyField(Quadranym, related_name="states")
    subs = models.CharField(max_length=32, blank=True)
    depth = models.PositiveSmallIntegerField(default=0)

    def enqode_fortune(self):
        'enqode fortune: grab-all q, enqode, reset q w/ only enqoding Qs'

        indx = 1
        out = self.body
        self.qode = ''
        many, one = [], []

        # enqode multi-q
        for quad in self.q2.all():
            out, subs = quad.enqode(out, indx, True)
            if subs:
                indx += len(subs)
                many.append(quad)

        # enqode single-q
        for quad in self.q1.all():
            out, subs = quad.enqode(out, indx, True)
            if subs:
                indx += len(subs)
                one.append(quad)

        # do subs and save
        if self.body != out:
            self.qode = out
            subs = [x.group(2) for x in QN.finditer(out)]
            self.subs = ''.join(subs).upper() # quadrant substitutions
            self.depth = max([x[0] for x in QN.findall(out)]) # depth != len(subs)
            self.q2.clear()
            self.q1.clear()
            self.save()
            for quad in many:
                self.q2.add(quad)
            for quad in one:
                self.q1.add(quad)

        self.save()

    def spin_fortune(self, quadranyms):
        'spin Fortune with Quadranym list'

        return deqodes(quadranyms, self.qode, trace=True)

    def __str__(self):
        return f'<F{self.depth}|{self.body[:18]}>'

class Winner(models.Model):
    'Winner class: game player'

    by = models.CharField(max_length=32)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, blank=True, null=True)
    app = models.CharField(max_length=32)
    score = models.PositiveSmallIntegerField()
    round = models.PositiveSmallIntegerField()

    def __str__(self):
        return f'<W|{self.user}|{self.score}>'

####################
### QODE METHODS ###
def enqodes(q_list, text):
    'enqode via Quadranym list: FIFO'

    for i, q in enumerate(q_list, 1):
        text = q.enqode(text, i)
    return text

def deqodes(q_list, text, trace=False):
    'deqode via Quadranym list: FIFO; trace returns tuple(text, q, qode)'

    if not trace:

        # skip trace
        for i, q in enumerate(q_list, 1):
            text = q.deqode(text, i)
        return text

    # trace output
    out = []
    nu = text
    for i, q in enumerate(q_list, 1):
        nu = q.deqode(nu, i, trace=True)
        out.append((nu, q, text))
    return out

def pairspin(phras, quads, path=None, text=False, trace=False):
    'spin Quadranyms and Phrases via path (zipper by default); return [(txt, q, qode)]'

    spun = []
    quadlen = len(quads)-1
    phralen = len(phras)-1

    if path == 'qt':

        # Topic-spin
        for i, quad in enumerate(quads):
            for phra in phras:
                spun.append((phra.spin(quad, trace=trace), quad, phra))
            if not i == quadlen:
                spun.append(('', None, None))

    elif path == 'tq':

        # Tale-spin
        for i, phra in enumerate(phras):
            for quad in quads:
                spun.append((phra.spin(quad, trace=trace), quad, phra))
            if not i == phralen:
                spun.append(('', None, None))
    else:

        # Zipper
        lim = min(quadlen, phralen) + 1
        for i in range(lim):
            quad = quads[i]
            phra = phras[i]
            spun.append((phra.spin(quad, trace=trace), quad, phra))

    if not text:
        return spun
    return [x[0] for x in spun]

def turn(text, q1s, q2s):
    'turn enqode/deqode by dual Quadranym lists'

    # enqode by first list
    for i, quad in enumerate(q1s):
        text = quad.enqode(text, i)

    # deqode by second list
    for i, quad in enumerate(q2s):
        text = quad.deqode(text, i)

    return text

#######################
### GENERAL METHODS ###
def quadrant_search(word, quads):
    'full-quadrant word lookup/count'

    got = {}
    neros = dict(name=0, e=0, r=0, o=0, s=0) # quadrant log

    for q in quads:
        nyms = {q.name:'name', q.e:'e', q.r:'r', q.o:'o', q.s:'s'}

        if word in nyms:

            quadrant = nyms[word]
            neros[quadrant] += 1
            if not quadrant in got:
                got[quadrant] = [q]
            else:
                got[quadrant].append(q)

    return got, neros

def poly_search(word, polys):
    'dimensional word lookup/count'

    got = {}
    dims = {x:0 for x in range(1, 13)} # dimension log

    for p in polys:
        nyms = dict([(getattr(p, f'p{x}'), p.depth) for x in range(1, 13)] + [(p.name, p.depth)])

        if word in nyms:

            dim = nyms[word]
            dims[dim] += 1
            if not dim in got:
                got[dim] = [p]
            else:
                got[dim].append(p)

    return got, dims

def dimension_dict(commons):
    'nym dimensional dictionary'

    words = {}
    for common in commons:
        for nym in common.nyms(True):
            if not nym in words:
                words[nym] = {common}
            else:
                words[nym].add(common)
    return words

def word_freq(words, url):
    'word frequencies in URL'

    r = HTTP.request('GET', url)
    html = r.data
    if not html:
        return []

    freq = {}
    for word in words:
        total = html.count(word.encode('utf-8'))
        if total:
            freq[word] = total

    return sorted(freq.items(), key=lambda kv: kv[1], reverse=True)

def winners():
    'top winners'

    wins = thingify(Winner)
    user_dict = {win.user:0 for win in wins}
    for win in wins:
        user_dict[win.user] += win.score
    return [(y, x) for x, y in sorted(user_dict.items(), key=lambda kv: kv[1], reverse=True)]

def top_field(common, field='user', lim=7, sort=False):
    'most popular dimensions in a field'

    out = common.objects.values_list(field).annotate(ord=models.Count(field)).order_by('-ord')
    out = dict([(k, v) for k, v in out if k][:lim])
    if not sort:
        return out
    return sorted(out.items(), key=lambda kv: kv[1], reverse=True)

def alltop(field='user', lim=7):
    'top_field in [Phrase,Polymap,Polynym,Quadranym,Story]'

    crop = {}
    for common in (Phrase, Polymap, Polynym, Quadranym, Story):

        for what, score in top_field(common, field, lim).items():
            if not what:
                continue

            what = get_user_model().objects.get(pk=what) if not isinstance(what, str) else what
            if what not in crop:
                crop[what] = score
            else:
                crop[what] += score

    return [(y, x) for x, y in sorted(crop.items(), key=lambda kv: kv[1], reverse=True)[:lim]]

def fame(app):
    'high scoring users, scores and average points-per-round'

    hi = Winner.objects.filter(app=app).order_by('-score')
    fx = {x.user.username:x.score/float(x.round) for x in hi}
    fx = [(f'{y:.2f}', x) for x, y in sorted(fx.items(), key=lambda kv: kv[1], reverse=True)[:10]]
    hi = [(x.score, x.user.username) for x in hi[:10]]

    return hi, fx

def sections(commons, sup=None, thresh=0):
    'mine Common objects for intersections'

    sex = []
    used = {x.id:0 for x in commons}
    nyms = {x.id:set(x.nyms(named=True)) for x in commons} # dimension dict
    comb = [(a, b, ab) for a, b, ab in [
        (a, b, tuple(nyms[a.id].intersection(nyms[b.id]))) for a, b in combinations(commons, 2)] if ab]
    nyms = {k:len(v)-1 for k, v in nyms.items()}
    comb = [(a, b, ab) for a, b, ab in comb if len(ab) != nyms[a.id] and len(ab) != nyms[b.id]] if not sup else \
           [(a, b, ab) for a, b, ab in comb if len(ab) == nyms[a.id] or len(ab) == nyms[b.id]]

    for a, b, ab in comb:
        sex.append((f'{a.id}_{b.id}', a, ab, b))
        used[a.id] += 1
        used[b.id] += 1

    return [(x, a, ab, b) for x, a, ab, b in sex if used[a.id] > thresh and used[b.id] > thresh]

def unions(pids):
    'mine Polynyms for unions'

    polynyms = thingify(Polynym).filter(pk__in=pids)
    terms = {}
    deps = {}
    nams = {}
    areas = {}
    sources = {}

    for p in polynyms:

        if p.depth not in deps:         # DEPTH
            deps[p.depth] = 1
        elif p.depth:
            deps[p.depth] += 1

        if p.area not in areas:         # AREA
            areas[p.area] = 1
        elif p.area:
            areas[p.area] += 1

        if p.src not in sources:        # SRC
            sources[p.src] = 1
        elif p.src:
            sources[p.src] += 1

        if p.name not in nams:          # NAME
            nams[p.name] = 1
        else:
            nams[p.name] += 1

        for i in range(1, 13):      # P1 - P12
            word = getattr(p, f'p{i}').lower()
            if word in terms:
                terms[word] += 1
            elif word:
                terms[word] = 1

    return [f'<b>{k}</b><sup>{v}</sup>' if v > 1 else str(k) for k, v in sorted(nams.items())], \
           [f'<b>{k}</b><sup>{v}</sup>' if v > 1 else str(k) for k, v in sorted(deps.items())], \
           [f'<b>{k}</b><sup>{v}</sup>' if v > 1 else k for k, v in sorted(terms.items())],     \
           [f'<b>{k}</b><sup>{v}</sup>' if v > 1 else k for k, v in sorted(areas.items())],     \
           [f'<b>{k}</b><sup>{v}</sup>' if v > 1 else k for k, v in sorted(sources.items())],   \
            sum([p.depth for p in polynyms]), len(terms)

####################
### VIEW METHODS ###
def polyset_table(polys):
    'Polyset view table'

    depth = max([p.depth for p in polys])
    width = sum([p.depth for p in polys])
    tabl = [[p, p.p1, p.p2, p.p3, p.p4, p.p5, p.p6, p.p7, p.p8,
             p.p9, p.p10, p.p11, p.p12][:depth+1] for p in polys]
    return depth, width, tabl, list(range(depth))

def poly_systems(polys):
    'depth-order sort polynyms'

    poly_dict = {p.depth:[] for p in polys}
    for p in polys:
        poly_dict[p.depth].append(p)
    poly_dict = sorted(poly_dict.items())
    ttl = [f'{x}-nym' for x, y in poly_dict]
    part = len([p for p in polys if p.mode == 'part'])
    step = len([p for p in polys if p.mode == 'step'])
    typ = len([p for p in polys if p.mode == 'type'])
    return ttl, [y for x, y in poly_dict], part, step, typ

def findquad_table(word, qs):
    'find quadranym view table'

    got, neros = quadrant_search(word, qs)
    header = Quadranym.objects.get(name='~Topic~')
    sliderule = dict(name=0, e=1, r=2, o=3, s=4)
    last = [(got[x], sliderule[x]) for x in neros if x in got][-1][-1]
    quadranyms = []
    slide = 0
    rows = []

    for quadrant in neros:
        if not quadrant in got:
            continue

        quads = got[quadrant]
        quadranyms.extend(quads)
        if not rows:
            quads.insert(0, header)
        slide = sliderule[quadrant]
        if slide != 0 and slide == last:
            quads.append(header)

        for q in quads:
            q15 = (
                (q.name, 'DFDFDF'), (q.e, 'CFCFCF'), (q.r, 'BFBFBF'), (q.o, 'AFAFAF'), (q.s, '9F9F9F'),
                (q.name, '000000'), (q.e, '3F3F3F'), (q.r, '2F2F2F'), (q.o, '3F3F3F'), (q.s, '2F2F2F'),
                (q.name, '9F9F9F'), (q.e, 'AFAFAF'), (q.r, 'BFBFBF'), (q.o, 'CFCFCF'), (q.s, 'EFEFEF'),
            )
            rows.append(q15[slide:] + q15[:slide])

    return rows, neros, quadranyms

def findpoly_table(word, ps):
    'find polynym view table'

    got, dims = poly_search(word, ps)
    polynyms = []
    rows = []

    for dim in dims.keys():
        if not dim in got:
            continue

        for poly in got[dim]:

            words = poly.nyms(True)
            row = list(zip(words, GRAYS[:poly.depth+1])) * 36
            for slide in range(13, 26):
                if row[slide][0] == word:
                    row = row[slide - 13:]
                    polynyms.append(poly)
                    break
            rows.append(row[:26])

    return rows, dims, polynyms

def polytile_table(p, wdt, hgt, named):
    'polytile view table'

    dep = p.depth if not named else p.depth + 1
    row = list(zip(p.nyms(named), GRAYS[:dep])) * 37

    return [row[i:wdt+i] for i in list(range(hgt))]

def mappable():
    'pk of two matched-depths Polynyms'

    mapabu = {x:[] for x in range(2, 13)}
    for poly in thingify(Polynym):
        mapabu[poly.depth].append(poly)
    mapabu = {x:y for x, y in mapabu.items() if len(y) > 1} # at least 2 per P
    a, b = sample(choice(list(mapabu.values())), 2)
    return a.pk, b.pk

def shade(level):
    'level hue'

    hue = SHADES.get(level-level%2)
    hue = SHADES.get(level-level%5) if not hue else hue
    return ('GreenYellow' if level > 74 else 'DimGray') if not hue else hue

def do_dict(form_list):
    'dict from forms'

    data = [form.cleaned_data for form in form_list]
    return {k: v for d in data for k, v in d.items()}

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

#####################
### SPEED TESTING ###
# def timer(iters):
#    'speed check'
#
#    #q = orderfy(Quadranym)[34]#qode = 'I q1e_VBD the q2o_NNS to make q1s_NNS need q1r_VBG.'
#    ps = thingify(Polynym)
#    tic = time()
#    for i in range(iters):
#        sections(ps)
#    a_speed = time() - tic
#
#    tic = time()
#    for i in range(iters):
#        sexy(ps)
#    b_speed = time() - tic
#
#    print(f'A:{a_speed} vs. B:{b_speed}')
