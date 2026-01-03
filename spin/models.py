#!/usr/bin/env python
# encoding: utf-8
'''
models.py -- Nymology database model classes
'''
from itertools import combinations
from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
from vote.models import VoteModel

from .cached import QN, shade
from .concept import guess_mood
from .english import eat, retoke, inflect
from .managers import FortuneData, Picker, PhraseData, PolynymData, \
                      QuadranymData, QueueData, QuoteData, WinnerData
from .methods import deqodes, quad_spin


### COMMON ABSTRACT CLASS
class Common(VoteModel, models.Model):
    'Nymology base class'
    name = models.CharField(max_length=128)
    user = models.ForeignKey(get_user_model(), on_delete=models.DO_NOTHING, blank=True, null=True)
    src = models.CharField(max_length=128, blank=True, verbose_name='source')
    area = models.CharField(max_length=32, blank=True)
    wiki = models.CharField(max_length=128, blank=True, verbose_name='info')

    objects = models.Manager()
    data = Picker()

    class Meta:
        abstract = True
        ordering = ['name', 'src']

    @property
    def likes(self):
        return self.votes.count()

    @property
    def voters(self):
        return [get_user_model().objects.get(pk=x[0]).username for x in self.votes.user_ids()]

    def named(self):
        'string-escaped name'
        return self.name.replace(' ', '\ ')

    def whois(self):
        'which object name'
        return self.__class__.__name__.lower()

    def label(self):
        'which object name'
        return self.__class__.__name__

    def get_absolute_url(self, *args, **kwargs):
        return reverse(f'spin:{self.whois()}_detail', kwargs={'pk': self.pk})

### COMMON MODELS
class Fable(Common):
    'enqoded phrasal template (multi-topic)'
    qode = models.CharField(max_length=4096, unique=True)
    subs = models.CharField(max_length=32, blank=True)
    length = models.PositiveSmallIntegerField(default=0)
    width = models.PositiveSmallIntegerField(default=0)
    realm = models.CharField(max_length=32, blank=True)

    def label(self):
        return 'Tale Template'

    def spin(self, quadranyms):
        'spin Fable with Quadranym list'
        return deqodes(quadranyms, self.qode)

    def nyms(self):
        'all words in Fable'
        return [x.replace(',', '').replace('.', '') for x in self.qode.split()] # <<~~~ use string.punc/tokenize?

    def __str__(self):
        return f'<F{self.length}x{self.width}:{self.name}|{self.area}|{self.user}|{self.src}>'

class Phrase(Common):
    'enqoded phrasal template (single-topic)'
    qode = models.CharField(max_length=2048, unique=True)
    subs = models.CharField(max_length=32, blank=True)
    width = models.PositiveSmallIntegerField(default=0)
    realm = models.CharField(max_length=32, blank=True)

    objects = models.Manager()
    data = PhraseData()

    def label(self):
        return 'Phrase Template'

    def spin(self, quadranym):
        'spin Phrase with input Quadranym'
        return quadranym.deqode(self.qode)

    def nyms(self):
        'all words in Phrase'
        return [x.replace(',', '').replace('.', '') for x in self.qode.split()] # <<~~~ use string.punc/tokenize?

    def __str__(self):
        return f'<Ph{self.width}:{self.name}|{self.area}|{self.user}|{self.src}>'

class Guessanym(Common):
    'found Polynym guess'
    mode = models.CharField(max_length=8, blank=True)
    depth = models.PositiveSmallIntegerField()
    seen = models.BooleanField(default=False)
    word = models.CharField(max_length=128)
    sentence = models.CharField(max_length=2048)
    paragraph = models.CharField(max_length=2048)
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

    objects = models.Manager()
    data = PolynymData()

    class Meta:
        unique_together = ['name', 'depth', 'src', 'area', 'sentence', 'paragraph', 'wiki', 'word']

    def __str__(self):
        return f'<P{self.depth}:{self.name}|{self.mode}|{self.area}|{self.user}|{self.src}>'

    def nyms(self, named=False):
        'all nyms; named=True includes Guessanym name'
        if not named:
            return [x for x in [self.p1, self.p2, self.p3, self.p4, self.p5, self.p6,
                                self.p7, self.p8, self.p9, self.p10, self.p11, self.p12] if x]
        return [x for x in [self.name, self.p1, self.p2, self.p3, self.p4, self.p5, self.p6,
                            self.p7, self.p8, self.p9, self.p10, self.p11, self.p12] if x]

    def related_poly(self):
        'node-search current nodes'
        return Polynym.data.related(self.nyms(True), self.wiki)

    def related_quad(self):
        'node-search current nodes'
        return Quadranym.data.related(self.nyms(True), self.wiki)

class Polynym(Common):
    'idea set (multi-term system) node max depth 12; use comma-separated lists for synonym sets'
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

    objects = models.Manager()
    data = PolynymData()

    class Meta:
        unique_together = ['name', 'depth', 'src', 'area', 'wiki', 'p1', 'p2', 'p3',
                           'p4', 'p5', 'p6', 'p7', 'p8', 'p9', 'p10', 'p11', 'p12']

    def max_nym(self):
        'max chars of name or dimensions'
        return max([len(nym) for nym in self.nyms()])

    def nyms(self, named=False):
        'all nyms; named=True includes Polynym name'
        if not named:
            return [x for x in [self.p1, self.p2, self.p3, self.p4, self.p5, self.p6,
                                self.p7, self.p8, self.p9, self.p10, self.p11, self.p12] if x]
        return [x for x in [self.name, self.p1, self.p2, self.p3, self.p4, self.p5, self.p6,
                            self.p7, self.p8, self.p9, self.p10, self.p11, self.p12] if x]

    def names(self):
        'nyms(True) shortcut for templates'
        return self.nyms(True)

    def pairs(self, named=True):
        'all possible nym pairs'
        return list(combinations(self.nyms(named=named), 2))

    def triangles(self, named=True):
        'all possible triangles'
        return list(combinations(self.nyms(named=named), 3))

    def quadrangles(self, named=True):
        'all possible quadrangles'
        return list(combinations(self.nyms(named=named), 4))

    def sense(self, word, polys, emo=False):
        moods = {syn.split(',')[0]:syn for syn in self.nyms()} # split synsets
        emos = [(m, 0, 9, shade(2)) for m in moods.keys()] if not word else \
            [(m, v, v/5.0, shade(v)) for m, v in guess_mood(word.lower(), moods.values()) if v > 0]
        mood = 'none' if not emos or not word else emos[0][0] # moods
        emo = 'none' if not emos or not word else '/'.join(moods[mood].split(',')) # mood synset
        say = 'relates to' if not emo else 'makes me' if self.src == 'Paul Ekman' \
                        else 'relates to being' if self.src == '2DES' else 'feels like'
        say = '' if not word else f'{word.capitalize()} {say} {emo}.'
        return dict(word=word, poly=self, polys=polys, emos=emos, mood=mood, say=say)

    def __str__(self):
        return f'<P{self.depth}:{self.name}|{self.mode}|{self.area}|{self.user}|{self.src}>'

class Polymap(Common):
    'Polynym relationship'
    pa = models.ForeignKey(Polynym, related_name="pnym_a", on_delete=models.CASCADE)
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

    class Meta:
        unique_together = ['name', 'user']

    def rels(self):
        'relations as list of lists'
        return [x.split(',') for x in [self.r1, self.r2, self.r3, self.r4, self.r5, self.r6, \
                                       self.r7, self.r8, self.r9, self.r10, self.r11, self.r12] if x]

    def __str__(self):
        return f'<Pmap:{self.name}|{self.area}|{self.user}|{self.src}>'

    def label(self):
        return 'Polynym Map'

class Polyset(Common):
    'set of Polynyms'
    polynyms = models.ManyToManyField(Polynym)
    length = models.PositiveSmallIntegerField(default=0)
    width = models.PositiveSmallIntegerField(default=0)
    depth = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = ['name', 'user']

    def __str__(self):
        return f'<Pset{self.length}x{self.width}:{self.name}|{self.area}|{self.user}|{self.src}>'

    def label(self):
        return 'Polynym Set'

class Quadranym(Common):
    'sensibility model node'
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

    objects = models.Manager()
    data = QuadranymData()

    class Meta:
        unique_together = ['name', 'e', 'r', 'o', 's', 'pos']

    def enqode(self, text, number=1, subs=False):
        'Q-encoder: optional topic-number; subs=True -> text,subs'
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
        return out if not subs else (out, ''.join(neros).upper())

    def deqode(self, text, number=1, bold=True):
        'POS-sensitive Q-notation decoder (regex): input text, optional number'
        matches = list(QN.finditer(text))
        subs = []
        slide = 0
        for m in matches: # qode slide
            if int(m.group(1)) == number: # Q index only
                nu = m.group(2)
                nu = getattr(self, nu if nu != 'n' else 'name')
                nu = nu.capitalize() if m.start() == 0 or m.group(0)[0].isupper() else nu
                nu = nu if not bold or nu.startswith('<') else f'<b>{nu}</b>'
                i = m.start() - slide
                o = m.end() - slide
                text = f'{text[:i]}{nu}{text[o:]}'
                diff = len(m.group(0)) - len(nu)
                slide += diff
                o -= diff
                subs.append((i, o, nu, m.group(3))) # (in, out, new-uninflected, new-pos)
        slide = 0 # conjugal slide
        doc = eat(text)
        for i, o, un, pos in subs:
            nu = inflect(doc, un, pos) # get new POS
            nu = un if not nu else nu
            nu = nu if not un[0].isupper() else nu.capitalize()
            nu = nu if not bold or nu.startswith('<') else f'<b>{nu}</b>'
            i -= slide
            o -= slide
            text = f'{text[:i]}{nu}{text[o:]}'
            slide += len(un) - len(nu)
        return text.replace(" '", "'").replace(" n'", "n'").replace("' m","'m").replace("' v", "'v") # <<~ yikes

    def freq(self, text, omit=None):
        'mine text for current topic/quadrants, return Q-freq NEROS-tuple'
        text = [x for x in text.split() if not x in omit] if omit is not None else text.split()
        return [text.count(x) for x in [self.name, self.e, self.r, self.o, self.s]]

    def nyms(self, named=False):
        'all nyms; named=True includes Quadranym name'
        if not named:
            return [x for x in [self.e, self.r, self.o, self.s] if x]
        return [x for x in [self.name, self.e, self.r, self.o, self.s] if x]

    def names(self):
        'nyms(True) shortcut for templates'
        return self.nyms(True)

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

class Quadraset(Common):
    'set of Quadranyms'
    quadranyms = models.ManyToManyField(Quadranym)
    length = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = ['name', 'user']

    def __str__(self):
        return f'<Qset{self.length}:{self.name}|{self.area}|{self.user}|{self.src}>'

    def label(self):
        return 'Quadranym Set'

class Story(Common):
    'Story class: paired Phrase/Quadranym list; builds Storyline data'
    length = models.PositiveSmallIntegerField(default=0)
    realm = models.CharField(max_length=32, blank=True)

    class Meta:
        unique_together = ['name',]

    def pairs(self):
        'Phrase, Quadranym lists from related Storyline'
        quads = [q.quadranym for q in Storyline.objects.filter(story=self.pk)]
        phras = [q.phrase for q in Storyline.objects.filter(story=self.pk)]
        if len(phras) != len(quads):
            return [], []
        return phras, quads

    def tell(self):
        'tell Story by its Storyline Phrase and Quadranym lists'
        return quad_spin(*self.pairs())

    def __str__(self):
        return f'<S{self.length}:{self.name}|{self.area}|{self.user}|{self.src}>'

class Storyline(models.Model):
    'Story plot line'
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    rank = models.PositiveSmallIntegerField()
    phrase = models.ForeignKey(Phrase, on_delete=models.CASCADE)
    quadranym = models.ForeignKey(Quadranym, on_delete=models.CASCADE)

class Tale(Common):
    'user-spun Fable; builds Taleline data'
    length = models.PositiveSmallIntegerField(default=0)
    fable = models.ForeignKey(Fable, related_name="fable", on_delete=models.CASCADE)

    class Meta:
        unique_together = ['name',]

    def quads(self):
        'associated Taleline Quadranym list'
        return [q.quadranym for q in Taleline.objects.filter(tale=self.pk)]

    def tell(self):
        'tell Tale by its Fable and Taleline Quadranym list'
        return deqodes(self.quads(), self.fable.qode)

    def __str__(self):
        return f'<T{self.length}:{self.name}|{self.area}|{self.user}|{self.src}>'

class Taleline(models.Model):
    'Tale plot line'
    tale = models.ForeignKey(Tale, on_delete=models.CASCADE)
    rank = models.PositiveSmallIntegerField()
    quadranym = models.ForeignKey(Quadranym, on_delete=models.CASCADE)

class Vectornym(Common):
    'Polynym vector'
    length = models.PositiveSmallIntegerField(default=0)
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

    class Meta:
        unique_together = ['name', 'user']

    def label(self):
        return 'Polynym Vector'

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

## UNCOMMON MODELS
class Fortune(models.Model):
    'Fortune class: enqoded quotes and sayings: NOT USER-ADDED'
    body = models.CharField(max_length=2048)
    qode = models.CharField(max_length=2048, blank=True)
    q1 = models.ManyToManyField(Quadranym)
    q2 = models.ManyToManyField(Quadranym, related_name="states")
    subs = models.CharField(max_length=32, blank=True)
    depth = models.PositiveSmallIntegerField(default=0)

    objects = models.Manager()
    data = FortuneData()

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
        return deqodes(quadranyms, self.qode)

    def __str__(self):
        return f'<F{self.depth}|{self.body[:18]}>'

class Queue(models.Model):
    'Quadranyms to-do list'
    name = models.CharField(max_length=128, unique=True)

    objects = models.Manager()
    data = QueueData()

    def __str__(self):
        return f'<Queue:{self.name}>'

class Quote(models.Model):
    'enqoded Quote: NOT USER-ADDED'
    body = models.CharField(max_length=2048)
    qode = models.CharField(max_length=2048, blank=True)
    quadranym = models.ForeignKey(Quadranym, on_delete=models.CASCADE)
    subs = models.CharField(max_length=32, blank=True)
    width = models.PositiveSmallIntegerField(default=0)
    src = models.CharField(max_length=128)

    objects = models.Manager()
    data = QuoteData()

    def spin_quote(self, quadranym):
        'spin Quote with Quadranym'
        return quadranym.deqode(self.qode)

    def unqode(self):
        'spin Quote with empty Quadranym'
        return Quadranym.objects.get(name='--').deqode(self.qode)

    def __str__(self):
        return f'<Quote:{self.width}|{self.subs}|{self.src}>'

class Winner(models.Model):
    'Winner class: game player: NOT DIRECTLY USER-ADDED'
    by = models.CharField(max_length=32) # remove
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, blank=True, null=True)
    app = models.CharField(max_length=32)
    score = models.PositiveSmallIntegerField()
    round = models.PositiveSmallIntegerField() # rename -> "move"

    data = WinnerData()

    def __str__(self):
        return f'<W|{self.user}|{self.score}>'

COMMON = dict(
    fable=Fable,
    guessanym=Guessanym,
    phrase=Phrase,
    polynym=Polynym,
    polymap=Polymap, # pa/pb ~> Polynym
    polyset=Polyset, # polynyms ~> [Polynym]
    quadranym=Quadranym,
    quadraset=Quadraset, # quadranyms ~> [Quadranym]
    story=Story,
    tale=Tale, # fable ~> Fable
    vectornym=Vectornym # v1-9 ~> Polynym
)
UNCOMMON = dict(
    fortune=Fortune, # q1/q2 ~> [Quadranym]
    queue=Queue,
    quote=Quote, # quadranym ~> Quadranym
    storyline=Storyline, # story/phrase/quadranym ~> Story/Phrase/Quadranym
    taleline=Taleline, # tale/quadranym ~> Tale/Quadranym
    winner=Winner, # user ~> User
)
