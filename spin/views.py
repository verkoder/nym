#!/usr/bin/env python
# encoding: utf-8
'''
views.py -- Nymology Django view classes & methods
'''

from itertools import product
from random import choice, sample
from django.db.models import Q
from django.db.models.functions import Length, Lower
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView, View
from django_tables2 import SingleTableView
#from rest_framework.decorators import api_view # API test
#from rest_framework.response import Response   # API test

from .cached import BENNETT, FEEL_SITE, shade
from .charts import depth_rng, depth_modes, field_dist, nym_wheel, nym_graph, polar, wordcloud
from .concept import RELATIONS, guess_fit
from .forms import QuadranymForm, PolynymForm, FableForm, PhraseForm, PolymapForm, reform, \
                   QuadrasetForm, PolysetForm, QueueForm, StoryForm, TaleForm, VectornymForm
from .games import fame, quiz
from .makers import story_menu, story_list, story_pair, tale_menu, tale_list
from .methods import deqodes, poly_tile, polyset_table, quad_spin, quad_turn, word_freq
from .models import COMMON, Common, Fable, Fortune, Guessanym, Phrase, Polymap, Polynym, Polyset, Quadranym, \
                    Quadraset, Queue, Quote, Story, Storyline, Tale, Taleline, Vectornym, Winner
from .permissions import BaseViewSet
from .serializers import FableSerializer, FortuneSerializer, PhraseSerializer, PolynymSerializer, \
                         PolymapSerializer, PolysetSerializer, \
                         QuadranymSerializer, QuadranymPicker, QuadrasetSerializer, \
                         QueueSerializer, QuoteSerializer, StorySerializer, StorylineSerializer, \
                         TaleSerializer, TalelineSerializer, VectornymSerializer, WinnerSerializer
from .stats import nymology_stats, playground_fun, user_stats
from .tables import PolynymTable, QuadranymTable

# SIMPLE VIEWS
def index_vu(request):
    return render(request, 'index.html', nymology_stats())
def info_api(request):
    return render(request, 'info/api.html')
def taper_vu(request):
    return render(request, 'flip/taper.html')
def info_site(request):
    return render(request, 'info/site.html', nymology_stats())
def play_vu(request):
    return render(request, 'play/playground.html',  playground_fun())
def user_vu(request, username=None):
    return render(request, 'info/user.html', user_stats(username))

class SignUp(CreateView):
    form_class = UserCreationForm
    success_url = '/accounts/login'
    template_name = 'registration/signup.html'

class CommonVote(LoginRequiredMixin, View):
    def get(self, request, com=None, io=None, pk=None):
        thing = get_object_or_404(COMMON[com], pk=pk)
        if io == 'u':
            thing.votes.up(request.user.pk)
        else:
            thing.votes.delete(request.user.pk)
        return redirect(f'/{com}/{pk}')

# COMMON BASE CLASS
class CommonDetail(DetailView):
    model = Common

    def __init__(self):
        self.template_name = f'see/{self.model.__name__.lower()}.html'

    def get(self, request, pk=None):
        things, thing = self.model.data.picks(pk=pk)
        return render(request, self.template_name,
                      dict(thing=thing, things=things,
                           msg='not found' if not thing and pk is not None else None))

    def post(self, request, *args, **kwargs):
        things, thing = self.model.data.picks(request)
        return render(request, self.template_name, dict(thing=thing, things=things))

class CommonCreate(LoginRequiredMixin, CreateView):
    model = Common
    template_name = 'add/common.html'
    dirty = []

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            return reform(form, self.dirty, request)
        return render(request, self.template_name, dict(form=form))

class CommonUpdate(LoginRequiredMixin, UpdateView):
    model = Common
    template_name = 'add/common.html'
    dirty = []

    def get(self, request, pk=None):
        form = self.form_class(instance=get_object_or_404(self.model, pk=pk))
        return render(request, self.template_name, dict(form=form, pk=pk))

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST,
                               instance=get_object_or_404(self.model, pk=kwargs['pk']))
        if form.is_valid():
            return reform(form, self.dirty) # clean fields here
        return render(request, self.template_name, dict(form=form))

class CommonDelete(LoginRequiredMixin, DeleteView):
    model = Common
    template_name = 'add/delete.html'

    def __init__(self):
        self.success_url = reverse_lazy(f'spin:{self.model.__name__.lower()}_detail')

# FABLE CRUD
class FableDetail(CommonDetail):
    model = Fable

class FableCreate(CommonCreate):
    model = Fable
    form_class = FableForm
    template_name = 'add/fable.html'
    dirty = ['subs', 'length', 'width']

class FableUpdate(CommonUpdate):
    model = Fable
    form_class = FableForm
    template_name = 'add/fable.html'
    dirty = ['subs', 'length', 'width']

class FableDelete(CommonDelete):
    model = Fable

# PHRASE CRUD
class PhraseDetail(CommonDetail):
    model = Phrase

class PhraseCreate(CommonCreate):
    model = Phrase
    form_class = PhraseForm
    template_name = 'add/phrase.html'
    dirty = ['subs', 'width']

class PhraseUpdate(CommonUpdate):
    model = Phrase
    form_class = PhraseForm
    template_name = 'add/phrase.html'
    dirty = ['subs', 'width']

class PhraseDelete(CommonDelete):
    model = Phrase

# POLYNYM CRUD
class PolynymDetail(CommonDetail):
    model = Polynym

    def get(self, request, pk=None, area=None, src=None, n=None):
        area = area or request.GET.get('area')
        src = src or request.GET.get('src')
        if area is not None: # >> AREA
            polys, ttl, data = Polynym.data.systems(area=area.replace('-', ' '))
            return render(request, f'find/poly_area.html', dict(data=data, ttl=ttl, area=area.replace('-', ' ').title(),
                                                                areas=Polynym.data.top_field('area', 11)))
        if src is not None: # >> SOURCE
            polys, ttl, data = Polynym.data.systems(src=src.replace('-', ' '))
            return render(request, f'find/poly_src.html', dict(data=data, ttl=ttl, src=src.replace('-', ' ').title(),
                                                               sources=Polynym.data.top_field('src', 11)))
        if n is not None: # >> N-NYM
            polys, ttl, data = Polynym.data.systems(depth=n)
            ttl = (['Polynym'] + [i for i in range(1, n+1 if n != 1 else 13)]) if n != 1 else ttl
            return render(request, f'find/n.html', dict(polys=polys, n=n, data=None if n != 1 else data, ttl=ttl,
                                                        ben=BENNETT, polyad=BENNETT[n].title()))
        things = Polynym.data.all()
        thing = get_object_or_404(Polynym, pk=pk) if pk is not None else choice(things)
        return render(request, self.template_name,
                      dict(thing=thing, things=things,
                           msg='not found' if not thing and pk is not None else None))

class PolynymCreate(CommonCreate):
    model = Polynym
    form_class = PolynymForm
    template_name = 'add/polynym.html'
    dirty = ['depth']

class PolynymUpdate(CommonUpdate):
    model = Polynym
    form_class = PolynymForm
    template_name = 'add/polynym.html'
    dirty = ['depth']

class PolynymDelete(CommonDelete):
    model = Polynym

# POLYMAP CRUD
class PolymapDetail(CommonDetail):
    model = Polymap

@login_required
def polymap_add_vu(request):
    pk1, pk2 = Polynym.data.matched_pair() if not 'p1_id' in request.POST or not 'p2_id' in request.POST \
               else (request.POST['p1_id'], request.POST['p2_id'])
    return render(request, 'make/polymap_relate.html', dict(polys=Polynym.data.all(),
                                                            p1=Polynym.objects.get(pk=pk1),
                                                            p2=Polynym.objects.get(pk=pk2)))

@login_required
def polymap_add2_vu(request):
    request.session['p1_id'] = pk1 = request.POST['p1_id']
    request.session['p2_id'] = pk2 = request.POST['p2_id']
    p1 = Polynym.objects.get(pk=pk1)
    p2 = Polynym.objects.get(pk=pk2)
    if pk1 == pk2:
        return render(request, 'make/polymap_relate.html', dict(polys=Polynym.data.all(), msg='Same Polynym!'))
    return render(request, 'make/polymap_save.html', dict(polys=Polynym.data.all(), p1=p1, p2=p2, rels=RELATIONS,
                                                     rng=range(max(p1.depth, p2.depth))))

@login_required
def polymap_save_vu(request):
    pa = Polynym.objects.get(pk=request.session.get('p1_id'))
    pb = Polynym.objects.get(pk=request.session.get('p2_id'))
    form = PolymapForm(request.POST)
    if form.is_valid():
        thing = form.save(commit=False)
        thing.user = request.user
        thing.pa = pa
        thing.pb = pb
        thing.r1 = '' if not set(['r1', 'pa1', 'pb1']).issubset(request.POST) else f"{request.POST['pa1']},{request.POST['r1']},{request.POST['pb1']}"
        thing.r2 = '' if not set(['r2', 'pa2', 'pb2']).issubset(request.POST) else f"{request.POST['pa2']},{request.POST['r2']},{request.POST['pb2']}"
        thing.r3 = '' if not set(['r3', 'pa3', 'pb3']).issubset(request.POST) else f"{request.POST['pa3']},{request.POST['r3']},{request.POST['pb3']}"
        thing.r4 = '' if not set(['r4', 'pa4', 'pb4']).issubset(request.POST) else f"{request.POST['pa4']},{request.POST['r4']},{request.POST['pb4']}"
        thing.r5 = '' if not set(['r5', 'pa5', 'pb5']).issubset(request.POST) else f"{request.POST['pa5']},{request.POST['r5']},{request.POST['pb5']}"
        thing.r6 = '' if not set(['r6', 'pa6', 'pb6']).issubset(request.POST) else f"{request.POST['pa6']},{request.POST['r6']},{request.POST['pb6']}"
        thing.r7 = '' if not set(['r7', 'pa7', 'pb7']).issubset(request.POST) else f"{request.POST['pa7']},{request.POST['r7']},{request.POST['pb7']}"
        thing.r8 = '' if not set(['r8', 'pa8', 'pb8']).issubset(request.POST) else f"{request.POST['pa8']},{request.POST['r8']},{request.POST['pb8']}"
        thing.r9 = '' if not set(['r9', 'pa9', 'pb9']).issubset(request.POST) else f"{request.POST['pa9']},{request.POST['r9']},{request.POST['pb9']}"
        thing.r10 = '' if not set(['r10', 'pa10', 'pb10']).issubset(request.POST) else f"{request.POST['pa10']},{request.POST['r10']},{request.POST['pb10']}"
        thing.r11 = '' if not set(['r11', 'pa11', 'pb11']).issubset(request.POST) else f"{request.POST['pa11']},{request.POST['r11']},{request.POST['pb11']}"
        thing.r12 = '' if not set(['r12', 'pa12', 'pb12']).issubset(request.POST) else f"{request.POST['pa12']},{request.POST['r12']},{request.POST['pb12']}"
        thing.save()
        return render(request, 'see/polymap.html',
                      dict(thing=thing, things=Polymap.data.all(), msg='Thanks for the Polymap!'))
    return render(request, 'make/polymap_save.html', dict(polys=Polynym.data.all(), p1=pa, p2=pb, rels=RELATIONS,
                                                     rng=range(max(pa.depth, pb.depth)), msg='Name your Polymap'))

class PolymapDelete(CommonDelete):
    model = Polymap


# POLYSET CRUD
class PolysetDetail(CommonDetail):
    model = Polyset

    def get(self, request, pk=None):
        things, thing = Polyset.data.picks(pk=pk)
        depth, width, tabl, ns = polyset_table(thing.polynyms.all())
        return render(request, self.template_name,
                      dict(thing=thing, things=things,
                           depth=depth, width=width, tabl=tabl, ns=ns,
                           msg='not found' if not thing and pk is not None else None))

    def post(self, request, pk=None):
        things, thing = Polyset.data.picks(request, pk=pk)
        depth, width, tabl, ns = polyset_table(thing.polynyms.all())
        return render(request, self.template_name,
                      dict(thing=thing, things=things,
                           depth=depth, width=width, tabl=tabl, ns=ns))

class PolysetCreate(CommonCreate):
    model = Polyset
    form_class = PolysetForm
    template_name = 'add/polyset.html'
    dirty = ['length', 'depth', 'width']

class PolysetUpdate(CommonUpdate):
    model = Polyset
    form_class = PolysetForm
    template_name = 'add/polyset.html'
    dirty = ['subs', 'depth', 'width']

class PolysetDelete(CommonDelete):
    model = Polyset

# QUADRANYM CRUD
class QuadranymDetail(CommonDetail):
    model = Quadranym

class QuadranymCreate(CommonCreate):
    model = Quadranym
    form_class = QuadranymForm
    template_name = 'add/quadranym.html'

    def get(self, request, kind='conjugal'):
        form = self.form_class(data_list=Queue.data.suggest(Quadranym))
        return render(request, self.template_name, dict(form=form, qseen=Quadranym.data.suggest(Queue), kind=kind))

    def post(self, request, kind='conjugal'):
        form = self.form_class(request.POST, data_list=Queue.data.suggest(Quadranym)) # to-do Q-queue
        if form.is_valid():
            return reform(form, request=request)
        return render(request, self.template_name, dict(form=form, qseen=Quadranym.data.suggest(Queue), kind=kind))

class QuadranymUpdate(CommonUpdate):
    model = Quadranym
    form_class = QuadranymForm
    template_name = 'add/quadranym.html'

    def get(self, request, pk=None, kind='conjugal'):
        form = self.form_class(instance=get_object_or_404(self.model, pk=pk),
                               data_list=Queue.data.suggest(Quadranym))
        return render(request, self.template_name, dict(form=form, qseen=Quadranym.data.suggest(Queue), pk=pk))

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST,
                               instance=get_object_or_404(self.model, pk=kwargs['pk']),
                               data_list=Queue.data.suggest(Quadranym))
        if form.is_valid():
            return reform(form)
        return render(request, 'add/quadranym.html', dict(form=form, qseen=Quadranym.data.suggest(Queue)))

class QuadranymDelete(CommonDelete):
    model = Quadranym

# QUADRASET CRUD
class QuadrasetDetail(CommonDetail):
    model = Quadraset

class QuadrasetCreate(CommonCreate):
    model = Quadraset
    form_class = QuadrasetForm
    template_name = 'add/quadraset.html'
    dirty = ['length']

class QuadrasetUpdate(CommonUpdate):
    model = Quadraset
    form_class = QuadrasetForm
    template_name = 'add/quadraset.html'
    dirty = ['length']

class QuadrasetDelete(CommonDelete):
    model = Quadraset

# GUESSANYM
class GuessanymDetail(CommonDetail):
    model = Guessanym

    def get(self, request, pk=None, mark=None, what=None):
        things = (Guessanym.data.all() if (not what or what in ('all', 'None')) else 
                  Guessanym.data.filter(seen=True) if what == 'seen' else 
                  Guessanym.data.exclude(seen=True)).order_by(Lower('name'), 'depth', 'word')
        thing = get_object_or_404(Guessanym, pk=pk) if pk is not None else \
            choice(things) if things else choice(Guessanym.data.all())
        if mark is not None:
            thing.seen = not thing.seen
            thing.save()
        return render(request, self.template_name,
                      dict(thing=thing, things=things, what=what,
                           msg='not found' if not thing and pk is not None else None))

class GuessanymUse(PolynymCreate):
    template_name = 'add/guessanym.html'

    def get_initial(self):
        g = Guessanym.objects.get(pk=self.kwargs['pk'])
        g.seen = True
        g.save()
        return dict(name=g.name, depth=g.depth, wiki=g.wiki, sentence=g.sentence, paragraph=g.paragraph, word=g.word,
                    p1=g.p1, p2=g.p2, p3=g.p3, p4=g.p4, p5=g.p5, p6=g.p6, p7=g.p7,
                    p8=g.p8, p9=g.p9, p10=g.p10, p11=g.p11, p12=g.p12, traces=g.related_poly())

# GUESSAQUAD
class GuessaquadDetail(GuessanymDetail):
    def __init__(self):
        self.template_name = 'see/guessaquad.html'

    def get(self, request, pk=None, mark=None, what=None):
        gues = Guessanym.data.filter(depth=4)
        things = (gues if (not what or what in ('all', 'None')) else 
                  gues.filter(seen=True) if what == 'seen' else 
                  gues.exclude(seen=True)).order_by(Lower('name'), 'depth', 'word')
        thing = get_object_or_404(Guessanym, pk=pk) if pk is not None else choice(things) if things else choice(gues)
        if mark is not None:
            thing.seen = not thing.seen
            thing.save()
        return render(request, self.template_name,
                      dict(thing=thing, things=things, what=what,
                           msg='not found' if not thing and pk is not None else None))

class GuessaquadUse(QuadranymCreate):
    model = Quadranym
    form_class = QuadranymForm
    template_name = 'add/guessaquad.html'

    def get(self, request, pk=None, kind='conjugal'):
        g = Guessanym.objects.get(pk=pk)
        g.seen = True
        g.save()
        form = self.form_class(data_list=Queue.data.suggest(Quadranym))
        qd,sco = Quadranym.data.place_nodes((g.p1, g.p2, g.p3, g.p4))
        form.initial = dict(name=g.name, depth=g.depth, wiki=g.wiki, sentence=g.sentence, paragraph=g.paragraph, word=g.word,
                            e=qd['e'], r=qd['r'], o=qd['o'], s=qd['s'], traces=g.related_quad())
        return render(request, self.template_name, dict(form=form, qseen=Quadranym.data.suggest(Queue), kind=kind, pk=pk, sco=sco))

    def post(self, request, pk=None, kind='conjugal'):
        form = self.form_class(request.POST, data_list=Queue.data.suggest(Quadranym)) # to-do Q-queue
        if form.is_valid():
            return reform(form, request=request)
        return render(request, self.template_name, dict(form=form, qseen=Quadranym.data.suggest(Queue), kind=kind, pk=pk))

# QUEUE CREATE
@login_required
def queue_add_vu(request):
    if request.method == 'POST':
        form = QueueForm(request.POST)
        if form.is_valid():
            form.save()
            form = QuadranymForm(data_list=Queue.data.suggest(Quadranym))
            return render(request, 'add/quadranym.html', dict(form=form, qseen=Quadranym.data.suggest(Queue), kind='conjugal', msg='Thanks for the topic request!'))
    else:
        form = QueueForm()
    return render(request, 'add/queue.html', dict(form=form))

# STORY CRUD
class StoryDetail(CommonDetail):
    model = Story

@login_required
def story_menu_vu(request):
    return render(*story_menu(request))

@login_required
def story_pair_vu(request):
    return render(*story_pair(request))

@login_required
def story_list_vu(request):
    return render(*story_list(request))

@login_required
def story_save_vu(request):
    form = StoryForm(request.POST)
    if form.is_valid():
        thing = form.save()
        thing.user = request.user
        thing.save()
        pairs = zip([int(x) for x in request.POST['phra_ids'].split(',')],
                    [int(x) for x in request.POST['quad_ids'].split(',')])
        for rank, (phra_id, quad_id) in enumerate(pairs):
            storyline = Storyline(story=thing, rank=rank, phrase=Phrase.objects.get(pk=phra_id),
                                  quadranym=Quadranym.objects.get(pk=quad_id))
            storyline.save()
        return render(request, 'see/story.html', dict(thing=thing, things=Story.data.all(),
                                                      msg='Thanks for the Story!'))
    return render(request, 'make/story_save.html', dict(phra_ids=request.POST['phra_ids'], length=request.POST['length'],
                                                        quad_ids=request.POST['quad_ids'], form=form))

class StoryDelete(CommonDelete):
    model = Story

# TALE CRUD
class TaleDetail(CommonDetail):
    model = Tale

@login_required
def tale_add_vu(request):
    fabls, fabl = Fable.data.picks(request, 'fabl_id')
    if '_text' in request.POST: # text-based
        return render(request, 'make/tale_list.html', dict(fabl=fabl, quads=Quadranym.data.all()))
    if '_use' in request.POST: # menu-based
        return render(request, 'make/tale_menu.html', dict(fabl=fabl, quads=Quadranym.data.all()))
    return render(request, 'make/tale_fable.html', dict(fabl=fabl, fabls=fabls)) # pick Fable..

@login_required
def tale_menu_vu(request):
    return render(*tale_menu(request))

@login_required
def tale_list_vu(request):
    return render(*tale_list(request))

@login_required
def tale_save_vu(request):
    form = TaleForm(request.POST)
    if form.is_valid():
        thing = form.save(commit=False)
        thing.user = request.user
        thing.fable = Fable.objects.get(pk=request.POST['fabl_id'])
        thing.save()
        quad_ids = [int(x) for x in request.POST['quad_ids'].split(',')]
        for rank, quad_id in enumerate(quad_ids):
            taleline = Taleline(tale=thing, rank=rank, quadranym=Quadranym.objects.get(pk=quad_id))
            taleline.save()
        return render(request, 'see/tale.html',
                      dict(thing=thing, things=Tale.data.all(), msg='Thanks for the Tale!'))
    return render(request, 'make/story_save.html', dict(fabl_id=request.POST['fabl_id'], length=request.POST['length'],
                                                        quad_ids=request.POST['quad_ids'], form=form))

class TaleDelete(CommonDelete):
    model = Tale

# VECTORNYM CRUD
class VectornymDetail(CommonDetail):
    model = Vectornym

class VectornymCreate(CommonCreate):
    model = Vectornym
    form_class = VectornymForm
    template_name = 'add/vectornym.html'
    dirty = ['length', 'width', 'depth',
             'v1', 'v2', 'v3', 'v4', 'v5', 'v6', 'v7', 'v8', 'v9']

class VectornymUpdate(CommonUpdate):
    model = Vectornym
    form_class = VectornymForm
    template_name = 'add/vectornym.html'
    dirty = ['length', 'width', 'depth',
             'v1', 'v2', 'v3', 'v4', 'v5', 'v6', 'v7', 'v8', 'v9']

class VectornymDelete(CommonDelete):
    model = Vectornym

# POLYNYM METHOD VIEWS

def pfind_vu(request, name=None):
    words = sorted(list(set(sum([p.nyms(True) for p in Polynym.data.all()], []))))
    name = request.POST.get('word') if 'word' in request.POST else name
    if name is not None:
        names = [name, name.replace('-', ' ')]
        names.extend([names[0].title(), names[1].title(), names[0][0].upper() + names[0][1:],
                      names[1][0].upper() + names[1][1:], names[0].upper(), names[1].upper()]) # unslugify attempts
        for word in names:
            if word in words:
                break
        else:
            return render(request, 'find/polynym.html', dict(words=words, msg='Word not found!'))
    else:
        word = choice(list(words))
    rows, ns, things = Polynym.data.view_table(word)
    d = '+'.join([f'P_{ {x} }' if y != '1' else f'{ y }P_{ x }' for x, y in ns.items() if y])
    return render(request, 'find/polynym.html',
                  dict(word=word, words=words, rows=rows, ns=ns, things=things, d=f'{d}'))

def polymath_vu(request):
    polys, p1 = Polynym.data.picks(request, 'p1_id')
    polys, p2 = Polynym.data.picks(request, 'p2_id')
    a = set(p1.nyms())
    b = set(p2.nyms())
    equal = bool(a == b)
    section = sorted(list(a & b)) # intersection
    union = sorted(list(a | b)) # union
    symdif = sorted(list(a ^ b)) # symmetric difference
    a_b = sorted(list(a - b)) # difference a - b
    b_a = sorted(list(b - a)) # difference b - a
    asub = a.issubset(b) # subsets
    bsub = b.issubset(a)
    asup = a.issuperset(b) # supersets
    bsup = b.issuperset(a)
    prod = [f'({x}, {y})' for x, y in sorted(product(a, b))] # product
    return render(request, 'compare/polymath.html',
                  dict(polys=polys, p1=p1, p2=p2, anyms=list(a), bnyms=list(b),
                       equal=equal, section=section, union=union, symdif=symdif,
                       a_b=a_b, b_a=b_a, asub=asub, bsub=bsub, asup=asup, bsup=bsup, prod=prod))

def polytile_vu(request):
    polys, poly = Polynym.data.picks(request)
    named = request.POST.get('named', '')
    dep = poly.depth if not named == 'on' else poly.depth + 1
    wdt = 'dep' if not 'wdt' in request.POST else request.POST['wdt']
    hgt = 'dep' if not 'hgt' in request.POST else request.POST['hgt']
    rows = poly_tile(poly, int(wdt) if wdt != 'dep' else \
                           dep, int(hgt) if hgt != 'dep' else dep, bool(named == 'on'))
    return render(request, 'compare/polytile.html',
                  dict(poly=poly, polys=polys, rows=rows, dep=dep, wdt=wdt, hgt=hgt, named=named))

def section_vu(request):
    sex = Polynym.data.sections()#supr)    #supr = request.POST.get('supr')
    got = [x for x in sex if x[0] == request.POST.get('ab_id')]
    abid, a, ab, b = choice(sex) if not got or not 'ab_id' in request.POST else got[0]
    a_sides = [x for x in a.nyms() if not x in ab] # nonsections
    b_sides = [x for x in b.nyms() if not x in ab]
    a_cut = len(a_sides)//2 # nonsection L/R split point
    b_cut = len(b_sides)//2
    return render(request, 'compare/section.html',
                  dict(abs=sex, ab=ab, abid=abid, things=[b,a], #supr=supr,
                       n=a_sides[:a_cut], s=a_sides[a_cut:],
                       e=b_sides[:b_cut], w=b_sides[b_cut:]))

def union_vu(request):
    polys, things, poly_ids, _msg = Polynym.data.samples(request)
    nams, deps, terms, areas, sources, total, utotal = Polynym.data.unions(poly_ids)
    plen = len(poly_ids)
    drop_dim = ((total/utotal)-1)*100 # Convergence:    dimension
    drop_dep = ((plen/len(deps))-1)*100               # depth
    drop_area = ((plen/len(areas))-1)*100             # area
    drop_src = ((plen/len(sources))-1)*100            # source
    drop_top = ((plen/len(nams))-1)*100               # topic
    return render(request, 'compare/union.html',
                  dict(polys=polys, nams=nams, things=things,
                       poly_ids=poly_ids, deps=deps, terms=terms,
                       drop_dim=drop_dim, drop_dep=drop_dep,
                       drop_area=drop_area, drop_src=drop_src,
                       drop_top=drop_top, total=total, utotal=utotal,
                       areas=areas, sources=sources))

########## QUADRANYM METHOD VIEWS

def qfind_vu(request, name=None):
    quads = Quadranym.data.all()
    words = sorted(list(set(sum([q.nyms(True) for q in quads], []))))
    name = request.POST.get('word') if 'word' in request.POST else name
    if name is not None:
        word = name.replace('-', ' ') # unslugify
        quad = quads.filter(Q(name=word) | Q(e=word) | Q(r=word) | Q(o=word) | Q(s=word) \
                          | Q(name=name) | Q(e=name) | Q(r=name) | Q(o=name) | Q(s=name))
        if not quad:
            return render(request, 'find/quadranym.html', dict(words=words, msg='Word not found!'))
        quad = quad[0]
    else:
        word = choice(words)
    rows, neros, things = Quadranym.data.view_table(word)
    return render(request, 'find/quadranym.html',
                  dict(word=word, words=words, rows=rows, neros=neros, things=things))

def quadramath_vu(request):
    compare1 = request.POST.get('compare1', 'polynym')
    compare2 = request.POST.get('compare2', 'quadranym')
    thing1s, thing1 = COMMON[compare1].data.picks(request, 'pk1')
    thing2s, thing2 = COMMON[compare2].data.picks(request, 'pk2')
    return render(request, 'compare/quadramath.html',
                  dict(thing1=thing1, thing2=thing2, thing1s=thing1s, thing2s=thing2s,
                       compare1=compare1, compare2=compare2))

def quadratile_vu(request, name=None):
    quads, quad = Quadranym.data.picks(request)
    if name is not None:
        quad = quads.filter(name=name.replace('-', ' '))
        if not quad:
            return render(request, 'compare/quadratile.html',
                          dict(quads=quads, msg='Quadranym not found!'))
        quad = quad[0]
    eq = Quadranym.objects.filter(name=quad.e) | Quadranym.objects.filter(name__icontains=quad.e)
    rq = Quadranym.objects.filter(name=quad.r) | Quadranym.objects.filter(name__icontains=quad.r)
    oq = Quadranym.objects.filter(name=quad.o) | Quadranym.objects.filter(name__icontains=quad.o)
    sq = Quadranym.objects.filter(name=quad.s) | Quadranym.objects.filter(name__icontains=quad.s)
    return render(request, 'compare/quadratile.html', dict(quad=quad, quads=quads,
                                                    eq=None if not eq else eq[0],
                                                    rq=None if not rq else rq[0],
                                                    oq=None if not oq else oq[0],
                                                    sq=None if not sq else sq[0]))

########## FEEL

def feel_fmk_vu(request):
    poly = get_object_or_404(Polynym, name='~fmk')
    w1 = request.POST.get('word1', '')
    w2 = request.POST.get('word2', '')
    w3 = request.POST.get('word3', '')
    best = guess_fit((w1, w2, w3), poly.nyms()) if (w1 and w2 and w3) else \
                    [('pal', 4), ('prince', 19), ('shooter', 29)]
    return render(request, 'feel/fmk.html', dict(emos=[(m, v, v*4, shade(v)) for m, v in best]))

def feel_mood_vu(request):
    polys = Polynym.objects.filter(Q(name='mood') | Q(name='moodset')).order_by('depth', 'src', 'name')
    poly = Polynym.objects.get(name='mood', src='Paul Ekman') if not 'pk' in request.POST \
                      else get_object_or_404(Polynym, pk=request.POST['pk'])
    return render(request, 'feel/mood.html', poly.sense(request.POST.get('word', ''), polys, True))

def feel_polynym_vu(request):
    polys, poly = Polynym.data.picks(request)
    return render(request, 'feel/polynym.html', poly.sense(request.POST.get('word', ''), polys))

def feel_site_vu(request):
    if 'pk' in request.POST:
        url = request.POST['url']
        polys, things, poly_ids, _msg = Polynym.data.samples(request)
        nams, deps, terms, areas, sources, total, utotal = Polynym.data.unions(poly_ids)
        msg,freq = word_freq(nams, url)
        return render(request, 'feel/site.html',
                      dict(polys=polys, nams=nams, things=things, poly_ids=poly_ids,
                           deps=deps, terms=terms, url=url, freq=freq, msg=msg,
                           maxcount=1 if not freq else freq[0][1],
                           areas=areas, sources=sources))
    else:
        FEEL_SITE['polys'] = Polynym.data.all()
        FEEL_SITE['things'] = FEEL_SITE['polys'].filter(pk__in=FEEL_SITE['poly_ids'])
    return render(request, 'feel/site.html', FEEL_SITE)

# PLAY

def fame_vu(request, game='PolyPuzzle'):
    return render(request, 'play/fame.html', fame(game))

def polypuzzle_vu(request):
    poly = choice(Polynym.data.all())
    return quiz(request, 'PolyPuzzle', dict(points=poly.depth,
                                            clue=choice(poly.nyms()),
                                            poly=poly))

def quadrazone_vu(request):
    quad = choice(list(Quadranym.data.all()))
    clue = choice(quad.nyms())
    points = 3 if clue in (quad.r, quad.e) else 5
    return quiz(request, 'QuadraZone', dict(points=points,
                                            clue=clue,
                                            quad=quad))

def quizzection_vu(request):
    sex = Polynym.data.sections()
    got = [x for x in sex if x[0] == request.POST.get('abid')]
    abid, a, ab, b = choice(sex) if not got or not 'abid' in request.POST else got[0]
    a_sides = [x for x in a.nyms() if not x in ab] # nonsections
    b_sides = [x for x in b.nyms() if not x in ab]
    a_cut = len(a_sides)//2 # nonsection split sizes
    b_cut = len(b_sides)//2
    return quiz(request, 'QuizZection', dict(points=a.depth + b.depth,
                                             clue=choice(ab),  # A/B cut N-S/E-W
                                             abs=sex, ab=ab, abid=abid, things=[b,a],
                                             n=a_sides[:a_cut], s=a_sides[a_cut:],
                                             e=b_sides[:b_cut], w=b_sides[b_cut:]))

def thegist_vu(request):
    quote = choice(Quote.objects.exclude(subs__icontains='N'))
    quads = sample(list(Quadranym.data.exclude(pk=quote.quadranym.pk)), choice((2, 3, 4)))
    quads.insert(choice(range(len(quads)+1)), quote.quadranym)
    return quiz(request, 'TheGist', dict(points=quote.width + len(quads),
                                         clue=quote.quadranym.pk,
                                         body=request.POST.get('body'),
                                         quote=quote,
                                         quads=quads))

def unquote_vu(request):
    quote = choice(Quote.objects.annotate(
                   bodylen=Length('body')).filter(bodylen__lt=101))
    quads = sample(list(Quadranym.data.exclude(pk=quote.quadranym.pk)), choice((2, 3, 4)))
    quads.insert(choice(range(len(quads)+1)), quote.quadranym)
    spin_quads = [(quote.spin_quote(q), q) for q in quads]
    return quiz(request, 'unQuote', dict(points=quote.width + len(quads),
                                         body=request.POST.get('body'),
                                         quads=quads, quote=quote,
                                         spin_quads=spin_quads))

# TELL
def tell_phrase_vu(request): # Phra x Quad
    phras, phra = Phrase.data.picks(request, 'phra_id')
    quads, quad = Quadranym.data.picks(request, 'quad_id')
    return render(request, 'tell/phrase.html',
                  dict(phras=sample(list(phras), 7), phra=phra, quad=quad,
                       quads=sample(list(quads), 7), spun=phra.spin(quad)))

def tell_tale_vu(request): # Fable x Quads
    rev = request.POST.get('rev')
    fabls, fabl = Fable.data.picks(request, 'fabl_id')
    quads, quadranyms, quad_ids, msg = Quadranym.data.samples(request, 'quad_id', fabl.length, rev)
    return render(request, 'tell/tale.html',
                  dict(quads=quads, fabls=fabls, spun=deqodes(quadranyms, fabl.qode),
                       topics=', '.join([x.name for x in quadranyms]),
                       quadranyms=quadranyms, fabl=fabl, quad_ids=quad_ids, rev=rev, msg=msg))

def tell_verse_vu(request): # Phras x Quads
    path = request.POST.get('path', 'tq')
    quads, quadranyms, quad_ids, _msg = Quadranym.data.samples(request, 'quad_id', 2)
    phras, phrases, phra_ids, _msg = Phrase.data.samples(request, 'phra_id', 2)
    spun, qode = quad_spin(phrases, quadranyms, path, qode=True)
    return render(request, 'tell/verse.html',
                  dict(phras=phras, quads=quads, phrases=phrases, quadranyms=quadranyms,
                       spun=spun, qode=qode, phra_ids=phra_ids, quad_ids=quad_ids, path=path))

# FLIP

def flip_fortune_vu(request): # Fort x Quads
    rev = request.POST.get('rev')
    forts, fort = Fortune.data.picks(request, 'fort_id')
    quads, targets, quad_ids, msg = Quadranym.data.samples(request, 'quad_id', fort.depth, rev)
    return render(request, 'flip/fortune.html',
                  dict(fort=fort, forts=forts, quads=quads, spun=fort.spin_fortune(targets),
                       quad_ids=quad_ids, targets=targets, rev=rev,
                       sources=list(set(fort.q2.all() | fort.q1.all())), msg=msg))

def flip_quote_vu(request, pk=None): # Quote x Quad
    quads, quad = Quadranym.data.picks(request, 'quad_id')
    quots, quot = Quote.data.picks(request, 'quot_id')
    if pk:
        quot = quots.get(pk=pk)
        quad = quot.quadranym
    return render(request, 'flip/quote.html',
                  dict(quots=quots, quads=quads, quot=quot, quad=quad, things=(quot,quad),
                       spun=quot.spin_quote(quad)))

def flip_text_vu(request): # text X Quads1 > Quads2
    quads, q1, q1_ids, _msg = Quadranym.data.samples(request, 'q1_id')
    quads, q2, q2_ids, _msg = Quadranym.data.samples(request, 'q2_id')
    q1_ids, q2_ids = (q1_ids, q2_ids) if request.method != 'GET' else ([], [])
    return render(request, 'flip/text.html', dict(txt=quad_turn(request.POST.get('txt'), q1, q2),
                                                   q1_ids=q2_ids, q2_ids=q1_ids, quads=quads))

# CHARTS

def plot_vu(request):
    typ = request.POST.get('typ', 'area_dist')
    ob = request.POST.get('ob', 'poly')
    ob = 'poly' if typ in ('sectionym', 'mode_dist', 'area_rng', 'src_rng', 'tilemap') else ob
    ob = 'poly' if typ == 'wordcloud' and ob not in ('poly', 'quad', 'fabl', 'phra') else ob
    ob = 'quad' if typ in ('realm_dist', 'polar') else ob
    return render(request, 'compare/plot.html', {'typ': typ, 'ob': ob})
def plot_poly_area_rng(request): # DEPTHS: poly
    return depth_rng(Polynym.data.all(), 'area')
def plot_poly_src_rng(request):
    return depth_rng(Polynym.data.all(), 'src')
def plot_poly_mode_deps(request):
    return depth_modes(Polynym.data.all())
def plot_poly_sectionym(request): # DEPENDENCY WHEEL: poly
    return nym_wheel(Polynym.data.sections(thresh=1))
def plot_poly_sectionet(request): # NETWORK GRAPH: poly/quad
    return nym_graph(Polynym.data.sections())
def plot_quad_sectionet(request):
    return nym_graph(Quadranym.data.sections())
def plot_quad_polar(request):     # POLAR: quad
    return polar(Quadranym.data.all())
def plot_poly_wordcloud(request): # WORDCLOUD: fabl/phra/poly/quad
    return wordcloud(Polynym.data.all(), 'Polynym')
def plot_quad_wordcloud(request):
    return wordcloud(Quadranym.data.all(), 'Quadranym')
def plot_phra_wordcloud(request):
    return wordcloud(Phrase.data.all(), 'Phrase')
def plot_fabl_wordcloud(request):
    return wordcloud(Fable.data.all(), 'Fable')
def plot_poly_mode_dist(request): # MODE DIST PIE: poly
    return field_dist(Polynym.data.all(), 'mode')
def plot_quad_realm_dist(request): # REALM DIST PIE: quad
    return field_dist(Quadranym.data.all(), 'realm')
def plot_tale_area_dist(request): # AREA DIST PIE: fabl/phra/poly/pmap/quad/stry/tale
    return field_dist(Tale.data.all(), 'area')
def plot_fabl_area_dist(request):
    return field_dist(Fable.data.all(), 'area')
def plot_stor_area_dist(request):
    return field_dist(Story.data.all(), 'area')
def plot_phra_area_dist(request):
    return field_dist(Phrase.data.all(), 'area')
def plot_poly_area_dist(request):
    return field_dist(Polynym.data.all(), 'area')
def plot_quad_area_dist(request):
    return field_dist(Quadranym.data.all(), 'area')
def plot_pmap_area_dist(request):
    return field_dist(Polymap.data.all(), 'area')
def plot_tale_src_dist(request):# SOURCE DIST PIE: fabl/phra/poly/pmap/quad/stry/tale
    return field_dist(Tale.data.all(), 'src')
def plot_fabl_src_dist(request):
    return field_dist(Fable.data.all(), 'src')
def plot_stor_src_dist(request):
    return field_dist(Story.data.all(), 'src')
def plot_phra_src_dist(request):
    return field_dist(Phrase.data.all(), 'src')
def plot_poly_src_dist(request):
    return field_dist(Polynym.data.all(), 'src')
def plot_quad_src_dist(request):
    return field_dist(Quadranym.data.all(), 'src')
def plot_pmap_src_dist(request):
    return field_dist(Polymap.data.all(), 'src')

# DATA TABLES
class QuadranymTabler(SingleTableView):
    model = Quadranym
    table_class = QuadranymTable
    template_name = 'see/commons.html'

class PolynymTabler(SingleTableView):
    model = Polynym
    table_class = PolynymTable
    template_name = 'see/commons.html'

# API VIEWSETS
class FableViewSet(BaseViewSet):
    'API endpoint: Fable'
    queryset = Fable.objects.order_by('name')
    serializer_class = FableSerializer

class FortuneViewSet(BaseViewSet):
    'API endpoint: Fortune'
    queryset = Fortune.objects.order_by('body')
    serializer_class = FortuneSerializer

class PhraseViewSet(BaseViewSet):
    'API endpoint: Phrase'
    queryset = Phrase.objects.order_by('name')
    serializer_class = PhraseSerializer

class PolynymViewSet(BaseViewSet):
    'API endpoint: Polynym'
    queryset = Polynym.objects.order_by('name', 'src')
    serializer_class = PolynymSerializer

class PolymapViewSet(BaseViewSet):
    'API endpoint: Polymap'
    queryset = Polymap.objects.order_by('name')
    serializer_class = PolymapSerializer

class PolysetViewSet(BaseViewSet):
    'API endpoint: Polyset'
    queryset = Polyset.objects.order_by('name')
    serializer_class = PolysetSerializer

class QuadranymViewSet(BaseViewSet):
    'API endpoint: Quadranym'
    queryset = Quadranym.objects.order_by('name')
    serializer_class = QuadranymSerializer

class QuadranymPicks(BaseViewSet):
    'API endpoint: Quadranym id, name'
    queryset = Quadranym.objects.order_by('name') #was#/.values_list('pk', 'name').order_by('name')
    serializer_class = QuadranymPicker

class QuadrasetViewSet(BaseViewSet):
    'API endpoint: Quadraset'
    queryset = Quadraset.objects.order_by('name')
    serializer_class = QuadrasetSerializer

class QueueViewSet(BaseViewSet):
    'API endpoint: Queue'
    queryset = Queue.objects.order_by('name')
    serializer_class = QueueSerializer

class QuoteViewSet(BaseViewSet):
    'API endpoint: Quote'
    queryset = Quote.objects.order_by('body')
    serializer_class = QuoteSerializer

class StoryViewSet(BaseViewSet):
    'API endpoint: Story'
    queryset = Story.objects.order_by('name')
    serializer_class = StorySerializer

class TaleViewSet(BaseViewSet):
    'API endpoint: Tale'
    queryset = Tale.objects.order_by('name')
    serializer_class = TaleSerializer

class StorylineViewSet(BaseViewSet):
    'API endpoint: Storyline'
    queryset = Storyline.objects.order_by('story')
    serializer_class = StorylineSerializer

class TalelineViewSet(BaseViewSet):
    'API endpoint: Taleline'
    queryset = Taleline.objects.order_by('tale')
    serializer_class = TalelineSerializer

class VectornymViewSet(BaseViewSet):
    'API endpoint: Vectornym'
    queryset = Vectornym.objects.order_by('name')
    serializer_class = VectornymSerializer

class WinnerViewSet(BaseViewSet):
    'API endpoint: Winner'
    queryset = Winner.data.order_by('app')
    serializer_class = WinnerSerializer

# @api_view()
# def yo_world(request, sup):
#     return Response({'mofo': 'yo mofo',
#                      'chachi': 'sup chachi'}[sup])
