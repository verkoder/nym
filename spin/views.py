"""
views.py -- Nymology Django view methods

Nymology by G.S Vercoe & D.C Scalise
Copyright (c) 2009-9999 Nymoholics Unlimited.
"""
import os.path
from itertools import product
from random import choice, sample
from django.db.models import Q
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
#from formtools.wizard.views import SessionWizardView

# NYMOLOGY CLASSES & METHODS
from .models import Common, Polynym, Polymap, Polyset, Quadranym, Quadraset, Queue, \
                    Fable, Phrase, Story, Storyline, Tale, Taleline, \
                    Fortune, Quote, Vectornym, Winner, \
                    sections, unions, mappable, orderfy, thingify, winners, \
                    findquad_table, findpoly_table, polytile_table, polyset_table, poly_systems, \
                    deqodes, pairspin, turn, word_freq, alltop, top_field, \
                    badge, fame, shade, \
                    NEWLINE, NEWLINE2, BENNETT#, do_dict
from .do_charts import depth_rng, depth_modes, field_dist, nym_wheel, nym_graph, wordcloud, polar
from .do_conceptnet import RELS, guess_mood, guess_fit
from .forms import QuadranymForm, PolynymForm, FableForm, PhraseForm, \
                   QuadrasetForm, PolysetForm, QueueForm, reform

# COMMON CLASS LOOKUP
COMMON = dict(
    fable=Fable,
    phrase=Phrase,
    polynym=Polynym,
    polymap=Polymap,
    polyset=Polyset,
    quadranym=Quadranym,
    quadraset=Quadraset,
    story=Story,
    tale=Tale,
    vectornym=Vectornym
)

def index_vu(request):
    'Nymology home & stats'

    return render(request, 'index.html', dict(
        top_poly=Polynym.objects.order_by('-votes')[:10],
        top_quad=Quadranym.objects.order_by('-votes')[:10],
        top_stor=Story.objects.order_by('-votes')[0],
        top_tale=Tale.objects.order_by('-votes')[0],
        pmaps=Polymap.objects.count(),
        polys=Polynym.objects.count(),
        tales=Tale.objects.count(),
        quads=Quadranym.objects.count(),
        phras=Phrase.objects.count(),
        stors=Story.objects.count(),
        fabls=Fable.objects.count(),
        areas=alltop('area'),
        sources=alltop('src'),
        users=alltop(),
        wins=winners()))

def user_vu(request, username=None):
    'Nymology user profile'

    usrs = get_user_model().objects.all()
    usr = usrs.filter(username=username)[0]
    msg = f'No user named "{usr}"' if not usr else None
    votes = {}
    nyms = {}
    for com, thing in COMMON.items():
        votes[com] = [x.name for x in thing.votes.all(usr.pk)]
        nyms[com] = [x.name for x in thing.objects.filter(user=usr)]
    total_votes = sum([len(x) for x in votes.values()])
    total_nyms = sum([len(x) for x in nyms.values()])
    wins = dict(puz=Winner.objects.filter(user=usr, app='puz'),
                sec=Winner.objects.filter(user=usr, app='sec'))
    total_wins = (0 if not wins['puz'] else wins['puz'][0].score) \
               + (0 if not wins['sec'] else wins['sec'][0].score)
    grand = total_votes + total_nyms + total_wins
    return render(request, 'registration/user.html',
                  dict(usr=usr, usrs=sample(list(usrs), 3),
                       wins=wins, grand=grand, votes=votes.items(), nyms=nyms.items(),
                       total_wins=total_wins, total_votes=total_votes, total_nyms=total_nyms,
                       earn=badge(grand), msg=msg))

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

#######################
##### COMMON CRUD #####
class CommonDetail(DetailView):
    model = Common

    def __init__(self):
        self.template_name = f'see/{self.model.__name__.lower()}.html'

    def get(self, request, pk=None):
        things = orderfy(self.model)
        thing = things.get(pk=pk) if pk is not None else choice(things)
        return render(request, self.template_name,
                      dict(thing=thing, things=things,
                           msg='not found' if not thing and pk is not None else None))

    def post(self, request, *args, **kwargs):
        things = orderfy(self.model)
        pk = request.POST.get('pk')
        thing = things.get(pk=pk) if pk is not None else choice(things)
        return render(request, self.template_name, dict(thing=thing, things=things))

class CommonTraceDetail(CommonDetail):
    def post(self, request, pk=None):
        things = orderfy(self.model)
        pk = request.POST.get('pk')
        thing = things.get(pk=pk) if pk is not None else choice(things)
        return render(request, self.template_name,
                      dict(thing=thing, things=things, trace=request.POST.get('trace')))

class CommonCreate(LoginRequiredMixin, CreateView):
    model = Common
    dirty = []

    # def __init__(self):
    #    name = f'add/{self.model.__name__.lower()}.html' # use common if no special template
    #    self.template_name = name if os.path.exists(f'templates/{name}') else 'add/common.html'

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            return reform(form, self.dirty, request)
        return render(request, self.template_name, dict(form=form))

class CommonUpdate(LoginRequiredMixin, UpdateView):
    model = Common
    dirty = []

    # def __init__(self):
    #    name = f'add/{self.model.__name__.lower()}.html' # use common if no special template
    #    self.template_name = name if os.path.exists(f'templates/{name}') else 'add/common.html'

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

########################
##### POLYNYM CRUD #####
class PolynymDetail(CommonDetail):
    model = Polynym

    def get(self, request, pk=None, area=None, src=None, n=None):

        # AREA
        if area is not None:
            polys = orderfy(Polynym).filter(area__iexact=area) if area != 'all' \
               else orderfy(Polynym)
            ttl, poly_dict, part, step, typ = poly_systems(polys)
            return render(request, f'find/poly_area.html',
                          dict(poly_dict=poly_dict, ttl=ttl, length=len(polys),
                               area=area, areas=top_field(Polynym, 'area', 11),
                               part=part, step=step, type=typ))
        # SOURCE
        if src is not None:
            polys = orderfy(Polynym).filter(src__icontains=src.replace('-', ' ')) if src != 'all' \
               else orderfy(Polynym)
            ttl, poly_dict, part, step, typ = poly_systems(polys)
            return render(request, f'find/poly_src.html',
                          dict(poly_dict=poly_dict, ttl=ttl, src=src, length=len(polys),
                               sources=top_field(Polynym, 'src', 11),
                               part=part, step=step, type=typ))
        # N-NYM
        if n is not None:
            polys = orderfy(Polynym, n) if n != 1 else orderfy(Polynym)
            ttl, poly_dict, part, step, typ = poly_systems(polys)
            ttl = (['Name'] + [f'p{i}' for i in range(1, n+1 if n != 1 else 13)]) if n != 1 else ttl
            return render(request, f'find/n.html',
                          dict(polys=polys, n=n, poly_dict=None if n != 1 else poly_dict, ttl=ttl,
                               part=part, step=step, type=typ, ben=BENNETT, ad=BENNETT[n].title()))
        # DETAIL
        things = orderfy(self.model)
        thing = things.get(pk=pk) if pk is not None else choice(things)
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

##########################
##### QUADRANYM CRUD #####
class QuadranymDetail(CommonDetail):
    model = Quadranym

class QuadranymCreate(CommonCreate):
    model = Quadranym
    template_name = 'add/quadranym.html'
    form_class = QuadranymForm

    def get(self, request, kind='conjugal'):
        form = self.form_class(data_list=orderfy(Queue))
        return render(request, self.template_name, dict(form=form, qseen=orderfy(), kind=kind))

    def post(self, request, kind='conjugal'):
        form = self.form_class(request.POST, data_list=orderfy(Queue)) # to-do Q-queue
        if form.is_valid():
            return reform(form, request=request)
        return render(request, self.template_name, dict(form=form, qseen=orderfy(), kind=kind))

class QuadranymUpdate(CommonUpdate):
    model = Quadranym
    template_name = 'add/quadranym.html'
    form_class = QuadranymForm

    def get(self, request, pk=None):
        form = self.form_class(instance=get_object_or_404(self.model, pk=pk),
                               data_list=orderfy(Queue))
        return render(request, self.template_name, dict(form=form, qseen=orderfy(), pk=pk))

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST,
                               instance=get_object_or_404(self.model, pk=kwargs['pk']),
                               data_list=orderfy(Queue))
        if form.is_valid():
            return reform(form)
        return render(request, 'add/quadranym.html', dict(form=form, qseen=orderfy()))

class QuadranymDelete(CommonDelete):
    model = Quadranym

#######################
##### PHRASE CRUD #####
class PhraseDetail(CommonDetail):
    model = Phrase

class PhraseCreate(CommonCreate):
    model = Phrase
    form_class = PhraseForm
    template_name = 'add/common.html'
    dirty = ['subs', 'width']

class PhraseUpdate(CommonUpdate):
    model = Phrase
    form_class = PhraseForm
    template_name = 'add/common.html'
    dirty = ['subs', 'width']

class PhraseDelete(CommonDelete):
    model = Phrase

#######################
##### FABLE CRUD #####
class FableDetail(CommonDetail):
    model = Fable

class FableCreate(CommonCreate):
    model = Fable
    form_class = FableForm
    template_name = 'add/common.html'
    dirty = ['subs', 'width']

class FableUpdate(CommonUpdate):
    model = Fable
    form_class = FableForm
    template_name = 'add/common.html'
    dirty = ['subs', 'width']

class FableDelete(CommonDelete):
    model = Fable

#####################
##### TALE CRUD #####
class TaleDetail(CommonTraceDetail):
    model = Tale

@login_required
def tale_add_vu(request):
    fabls = orderfy(Fable)
    fabl = choice(fabls) if not 'fabl_id' in request.POST else \
                 get_object_or_404(Fable, pk=request.POST['fabl_id'])
    if '_text' in request.POST: # text-based pusher..
        return render(request, 'add/tale2b.html', dict(fabl=fabl, quads=orderfy(Quadranym)))
    if '_use' in request.POST: # user picks fable..
        return render(request, 'add/tale2.html', dict(fabl=fabl, quads=orderfy(Quadranym)))
    return render(request, 'add/tale.html', dict(fabl=fabl, fabls=fabls))

@login_required
def tale_a2d_vu(request):
    'Frame-by-Frame Tale-pusher'

    fabl = get_object_or_404(Fable, pk=request.POST['fabl_id'])
    quad_id = None if not 'quad_id' in request.POST else int(request.POST['quad_id'])
    quad_ids = [] if not 'quad_ids' in request.POST else \
                      [int(x) for x in request.POST.get('quad_ids').split(',') if x]
    if quad_id and not '_save' in request.POST:
        quad_ids.append(quad_id)
    tale_dict = {q.pk:q for q in Quadranym.objects.filter(pk__in=quad_ids)}
    tale_quads = [tale_dict[qid] for qid in quad_ids] # avoid hitting db for each
    trace = request.POST.get('trace')
    spun = deqodes(tale_quads, fabl.qode, trace=trace)
    tops = [q.name for q in tale_quads]
    if quad_ids and '_try' in request.POST:
        tops.pop()
        quad_ids.pop()
    togo = fabl.length - len(quad_ids)
    msg = f'Add {togo} topics!' if togo != 1 else 'Add last topic!'
    quad_ids = ','.join([str(x) for x in quad_ids])
    if togo != 0:
        return render(request, 'add/tale2.html',
                      dict(spun=spun, quads=orderfy(Quadranym),
                           tale_quads=tale_quads, tops=tops, fabl=fabl,
                           quad_id=quad_id,
                           quad_ids=quad_ids, msg=msg, trace=trace))
    spun = spun[-1][0] if isinstance(spun[0], tuple) else spun # omit trace
    return render(request, 'add/tale3.html',
                  dict(spun=spun, quad_ids=quad_ids, fabl=fabl,
                       d_src=fabl.src, d_area=fabl.area, d_url=fabl.wiki, quad_txt=', '.join(tops)))

@login_required
def tale_a2b_vu(request):
    'Topic-list Tale-pusher'

    msg = ''
    quad_txt = request.POST.get('quad_txt', '').strip()
    fabl = get_object_or_404(Fable, pk=request.POST['fabl_id'])
    quad_names = quad_txt.split(',')
    tale_dict = {q.name:q for q in Quadranym.objects.filter(name__in=quad_names)}
    tale_quads = [tale_dict.get(name) for name in quad_names] # avoid hitting db for each
    if None in tale_quads:
        msg = ', '.join([x for x in [quad_names[i] if not q else \
            None for i, q in enumerate(tale_quads)] if x is not None])
        msg = f"Oops! Can't find [{msg}] "
        tale_quads = [x for x in tale_quads if x]
    msg += 'Not enough topics!' if len(tale_quads) < fabl.length else 'Too many topics!' \
                                if len(tale_quads) > fabl.length else None if not quad_txt else msg
    trace = request.POST.get('trace')
    spun = None if not quad_txt else deqodes(tale_quads, fabl.qode, trace=trace)
    if not '_save' in request.POST:
        return render(request, 'add/tale2b.html',
                      dict(spun=spun, quads=orderfy(Quadranym),
                           tale_quads=tale_quads, fabl=fabl,
                           quad_txt=quad_txt, msg=msg, trace=trace))
    quad_ids = ','.join([str(q.pk) for q in tale_quads])
    spun = spun[-1][0] if isinstance(spun[0], tuple) else spun # omit trace
    return render(request, 'add/tale3.html',
                  dict(spun=spun, quad_ids=quad_ids, fabl=fabl, d_src=fabl.src,
                       d_area=fabl.area, d_url=fabl.wiki, quad_txt=quad_txt))

@login_required
def tale_save_vu(request):
    thing = Tale(
        name=request.POST['name'],
        user=request.user,
        src=request.POST['src'],
        wiki=request.POST['wiki'],
        area=request.POST['area'],
        length=request.POST['length'],
        fable=Fable.objects.get(pk=request.POST['fabl_id'])
    )
    thing.save()
    quad_ids = [int(x) for x in request.POST['quad_ids'].split(',')]
    for rank, quad_id in enumerate(quad_ids):
        taleline = Taleline(tale=thing, rank=rank, quadranym=Quadranym.objects.get(pk=quad_id))
        taleline.save()
    return render(request, 'see/tale.html',
                  dict(thing=thing, things=orderfy(Tale), msg='Thanks for the Tale!'))

class TaleDelete(CommonDelete):
    model = Tale

######################
##### STORY CRUD #####
class StoryDetail(CommonTraceDetail):
    model = Story

@login_required
def story_add_vu(request):
    'Frame-by-Frame Story-pusher'

    phra_id = None if not 'phra_id' in request.POST else int(request.POST['phra_id'])
    quad_id = None if not 'quad_id' in request.POST else int(request.POST['quad_id'])
    phra_ids = [] if not 'phra_ids' in request.POST else \
                      [int(x) for x in request.POST.get('phra_ids').split(',') if x]
    quad_ids = [] if not 'quad_ids' in request.POST else \
                      [int(x) for x in request.POST.get('quad_ids').split(',') if x]
    if phra_id and quad_id and not '_save' in request.POST:
        quad_ids.append(quad_id)
        phra_ids.append(phra_id)
    stor_phras = [Phrase.objects.get(pk=pk) for pk in phra_ids]
    stor_quads = [Quadranym.objects.get(pk=pk) for pk in quad_ids]
    trace = request.POST.get('trace')
    spun = pairspin(stor_phras, stor_quads, trace=trace)
    if quad_ids and '_try' in request.POST:
        for undo in (stor_quads, stor_phras, quad_ids, phra_ids):
            undo.pop()
    phra_ids, quad_ids = ','.join([str(x) for x in phra_ids]), ','.join([str(x) for x in quad_ids])
    txt = '<br>'.join([f'{q} &nbsp; <font size="+3"><b>&harrw;</b></font> &nbsp; {p}' \
                       for q, p in zip([q.name for q in stor_quads], \
                                       [ph.name for ph in stor_phras])])
    if not '_save' in request.POST:
        return render(request, 'add/story.html',
                      dict(spun=spun, txt=txt, trace=trace,
                           quads=Quadranym.objects.all(), quad_id=quad_id, phra_id=phra_id,
                           phras=Phrase.objects.all(), quad_ids=quad_ids, phra_ids=phra_ids))
    return render(request, 'add/story2.html',
                  dict(spun=spun, txt=txt, quad_ids=quad_ids, phra_ids=phra_ids))

@login_required
def story_adb_vu(request):
    'Pair-List Story-pusher'

    msg = None
    txt = request.POST.get('txt', '').strip()
    _txt = [x.split(',') for x in NEWLINE.split(NEWLINE2.sub('\n-,-\n', txt)) if ',' in x]
    quad_names, phra_names = [x[0] for x in _txt], [x[1] for x in _txt]
    stor_quads = [q[0] for q in [Quadranym.objects.filter(name=n) for n in quad_names] if q]
    stor_phras = [ph[0] for ph in [Phrase.objects.filter(name=n) for n in phra_names] if ph]
    trace = request.POST.get('trace')
    spun = pairspin(stor_phras, stor_quads, trace=trace)
    if len(stor_quads) != len(quad_names) or len(stor_phras) != len(phra_names):
        msg = ', '.join([x for x in [quad_names[i] if len(q) == 0 else \
          None for i, q in enumerate([Quadranym.objects.filter(name=n) \
               for n in quad_names])] if x is not None] \
          + [x for x in [phra_names[i] if len(ph) == 0 else \
          None for i, ph in enumerate([Phrase.objects.filter(name=n) \
               for n in phra_names])] if x is not None])
        msg = f"Oops! Can't find [{msg}]"
    if not '_save' in request.POST:
        return render(request, 'add/storyb.html',
                      dict(spun=spun, txt=txt, quads=orderfy(Quadranym),
                           phras=orderfy(Phrase), msg=msg, trace=trace))
    txt = '<br>'.join([f'{q} &nbsp; <font size="+3"><b>&harrw;</b></font> &nbsp; {p}' \
                       for q, p in zip([q.name for q in stor_quads], \
                                     [ph.name for ph in stor_phras])])
    return render(request, 'add/story2.html',
                  dict(spun=spun, txt=txt, quad_ids=','.join([str(q.pk) for q in stor_quads]),
                       phra_ids=','.join([str(ph.pk) for ph in stor_phras])))

@login_required
def story_adc_vu(request):
    'Matched-Lists Story-pusher'
    msg = None
    quad_txt = request.POST.get('quad_txt', '').strip()
    phra_txt = request.POST.get('phra_txt', '').strip()
    quad_names = NEWLINE.sub(',-,', quad_txt).split(',')
    phra_names = NEWLINE.sub(',-,', phra_txt).split(',')
    if len(quad_names) > len(phra_names) == 1:
        phra_names = [phra_names[0] for x in range(len(quad_names))]
    elif len(phra_names) > len(quad_names) == 1:
        quad_names = [quad_names[0] for x in range(len(phra_names))]
    quad_dict = {q.name:q for q in \
                 Quadranym.objects.filter(name__in=list(set(quad_names)))} # ez on db
    phra_dict = {ph.name:ph for ph in Phrase.objects.filter(name__in=list(set(phra_names)))}
    stor_quads = [quad_dict.get(name) for name in quad_names if name]
    stor_phras = [phra_dict.get(name) for name in phra_names if name]
    if stor_quads and stor_phras and None in stor_quads or None in stor_phras:
        msg = ', '.join([x for x in [quad_names[i] if not q else None \
                           for i, q in enumerate(stor_quads)] if x is not None] \
                      + [x for x in [phra_names[i] if not ph else None \
                           for i, ph in enumerate(stor_phras)] if x is not None])
        msg = f"Oops! Can't find [{msg}]"
        stor_phras = [x for x in stor_phras if x] # patch user error
        stor_quads = [x for x in stor_quads if x]
    trace = request.POST.get('trace')
    spun = pairspin(stor_phras, stor_quads, trace=trace)
    if not '_save' in request.POST:
        return render(request, 'add/storyc.html',
                      dict(spun=spun, quad_txt=quad_txt, phra_txt=phra_txt,
                           quads=orderfy(Quadranym),
                           phras=orderfy(Phrase),
                           msg=msg, trace=trace))
    txt = '<br>'.join([f'{q} &nbsp; <font size="+3"><b>&harrw;</b></font> &nbsp; {p}' \
                       for q, p in zip([q.name for q in stor_quads], \
                                     [ph.name for ph in stor_phras])])
    return render(request, 'add/story2.html',
                  dict(spun=spun, txt=txt,
                       quad_ids=','.join([str(q.pk) for q in stor_quads]),
                       phra_ids=','.join([str(ph.pk) for ph in stor_phras])))

@login_required
def story_save_vu(request):
    thing = Story(
        name=request.POST['name'],
        user=request.user,
        src=request.POST['src'],
        wiki=request.POST['wiki'],
        area=request.POST['area'],
        length=request.POST['length'],
        realm=request.POST.get('realm', ''),
    )
    thing.save()
    pairs = zip([int(x) for x in request.POST['phra_ids'].split(',')],
                [int(x) for x in request.POST['quad_ids'].split(',')])
    for rank, (phra_id, quad_id) in enumerate(pairs):
        storyline = Storyline(story=thing, rank=rank, phrase=Phrase.objects.get(pk=phra_id),
                              quadranym=Quadranym.objects.get(pk=quad_id))
        storyline.save()
    return render(request, 'see/story.html', dict(thing=thing, things=orderfy(Story),
                                                  msg='Thanks for the Story!'))

class StoryDelete(CommonDelete):
    model = Story

########################
##### POLYMAP CRUD #####
class PolymapDetail(CommonDetail):
    model = Polymap

@login_required
def polymap_add_vu(request):
    if not 'p1_id' in request.POST or not 'p2_id' in request.POST:
        p1k, p2k = mappable()
    else:
        p1k = request.POST['p1_id']
        p2k = request.POST['p2_id']
    return render(request, 'add/polymap.html',
                  dict(polys=orderfy(Polynym),
                       p1=Polynym.objects.get(pk=p1k),
                       p2=Polynym.objects.get(pk=p2k)))

def polymap_adn_vu(request):
    p1k = request.POST['p1_id']
    p2k = request.POST['p2_id']
    request.session['p1_id'] = p1k
    request.session['p2_id'] = p2k
    a = Polynym.objects.get(pk=p1k)
    b = Polynym.objects.get(pk=p2k)
    if p1k == p2k:
        return render(request, 'add/polymap.html',
                      dict(polys=orderfy(Polynym), msg='Same Polynym!'))
    return render(request, 'add/polymap2.html',
                  dict(polys=orderfy(Polynym), p1=a, p2=b, rels=RELS,
                       rng=range(max(a.depth, b.depth))))

@login_required
def polymap_save_vu(request):
    thing = Polymap(
        name=request.POST['name'],
        user=request.user,
        src=request.POST['src'],
        wiki=request.POST['wiki'],
        area=request.POST['area'],
        pa=Polynym.objects.get(pk=request.session.get('p1_id')),
        pb=Polynym.objects.get(pk=request.session.get('p2_id')),
        r1='' if not set(['r1', 'pa1', 'pb1']).issubset(request.POST) else f"{request.POST['pa1']},{request.POST['r1']},{request.POST['pb1']}",
        r2='' if not set(['r2', 'pa2', 'pb2']).issubset(request.POST) else f"{request.POST['pa2']},{request.POST['r2']},{request.POST['pb2']}",
        r3='' if not set(['r3', 'pa3', 'pb3']).issubset(request.POST) else f"{request.POST['pa3']},{request.POST['r3']},{request.POST['pb3']}",
        r4='' if not set(['r4', 'pa4', 'pb4']).issubset(request.POST) else f"{request.POST['pa4']},{request.POST['r4']},{request.POST['pb4']}",
        r5='' if not set(['r5', 'pa5', 'pb5']).issubset(request.POST) else f"{request.POST['pa5']},{request.POST['r5']},{request.POST['pb5']}",
        r6='' if not set(['r6', 'pa6', 'pb6']).issubset(request.POST) else f"{request.POST['pa6']},{request.POST['r6']},{request.POST['pb6']}",
        r7='' if not set(['r7', 'pa7', 'pb7']).issubset(request.POST) else f"{request.POST['pa7']},{request.POST['r7']},{request.POST['pb7']}",
        r8='' if not set(['r8', 'pa8', 'pb8']).issubset(request.POST) else f"{request.POST['pa8']},{request.POST['r8']},{request.POST['pb8']}",
        r9='' if not set(['r9', 'pa9', 'pb9']).issubset(request.POST) else f"{request.POST['pa9']},{request.POST['r9']},{request.POST['pb9']}",
        r10='' if not set(['r10', 'pa10', 'pb10']).issubset(request.POST) else f"{request.POST['pa10']},{request.POST['r10']},{request.POST['pb10']}",
        r11='' if not set(['r11', 'pa11', 'pb11']).issubset(request.POST) else f"{request.POST['pa11']},{request.POST['r11']},{request.POST['pb11']}",
        r12='' if not set(['r12', 'pa12', 'pb12']).issubset(request.POST) else f"{request.POST['pa12']},{request.POST['r12']},{request.POST['pb12']}"
    )
    thing.save()
    return render(request, 'see/polymap.html',
                  dict(thing=thing, things=orderfy(Polymap), msg='Thanks for the Polymap!'))

class PolymapDelete(CommonDelete):
    model = Polymap

##########################
##### VECTORNYM CRUD #####
class VectornymDetail(CommonDetail):
    model = Vectornym

@login_required
def vectornym_add_vu(request):
    'Polynym List Vectornym-pusher'

    res = {f'v{i}':request.POST.get(f'v{i}') for i in range(1, 10)}
    res['length'] = len([x for x in res.values() if x])
    if res['length'] == 1:
        return render(request, 'add/vectornym.html',
                      dict(polys=orderfy(Polynym), msg='Need more nyms!'))
    if not res['v1'] and not res['length'] == 0:
        return render(request, 'add/vectornym.html',
                      dict(polys=orderfy(Polynym), msg='No first nym!'))
    spun = []
    width = 0
    depth = 0
    for i in range(1, 10):
        if not f'v{i}' in request.POST:
            break
        poly = Polynym.objects.get(pk=request.POST[f'v{i}'])
        spun.append((poly.name, poly.nyms(False)))
        width += poly.depth
        if poly.depth > depth:
            depth = poly.depth
    res['spun'] = spun
    res['width'] = width
    res['depth'] = depth
    if not '_save' in request.POST:
        return render(request, 'add/vectornym.html', dict(polys=orderfy(Polynym)))
    if not res['length'] == i - 1 and not i == 9:
        return render(request, 'add/vectornym.html',
                      dict(polys=orderfy(Polynym), msg='Noncontiguous nyms!'))
    return render(request, 'add/vectornym2.html', res)

@login_required
def vectornym_save_vu(request):
    thing = Vectornym(
        name=request.POST['name'],
        user=request.user,
        src=request.POST['src'],
        wiki=request.POST['wiki'],
        area=request.POST['area'],
        length=request.POST['length'],
        width=request.POST['width'],
        depth=request.POST['depth'],
        realm=request.POST.get('realm', ''))
    for i in range(1, 10):
        if f'v{i}' in request.POST:
            thing.__setattr__(f'v{i}', Polynym.objects.get(pk=request.POST[f'v{i}']))
    thing.save()
    return render(request, 'see/vectornym.html',
                  dict(thing=thing, things=orderfy(Vectornym), msg='Thanks for the Vectornym!'))

class VectornymDelete(CommonDelete):
    model = Vectornym

########################
##### POLYSET CRUD #####
class PolysetDetail(CommonDetail):
    model = Polyset

    def get(self, request, pk=None):
        things = orderfy(self.model)
        thing = things.get(pk=pk) if pk is not None else choice(things)
        depth, width, tabl, ns = polyset_table(thing.polynyms.all())
        return render(request, self.template_name,
                      dict(thing=thing, things=things,
                           depth=depth, width=width, tabl=tabl, ns=ns,
                           msg='not found' if not thing and pk is not None else None))
    def post(self, request, pk=None):
        things = orderfy(self.model)
        thing = things.get(pk=request.POST.get('pk'))
        depth, width, tabl, ns = polyset_table(thing.polynyms.all())
        return render(request, self.template_name,
                      dict(thing=thing, things=things,
                           depth=depth, width=width, tabl=tabl, ns=ns))

class PolysetCreate(CommonCreate):
    model = Polyset
    form_class = PolysetForm
    template_name = 'add/common.html'
    dirty = ['length', 'depth', 'width']

class PolysetUpdate(CommonUpdate):
    model = Polyset
    form_class = PolysetForm
    template_name = 'add/common.html'
    dirty = ['subs', 'depth', 'width']

class PolysetDelete(CommonDelete):
    model = Polyset

##########################
##### QUADRASET CRUD #####
class QuadrasetDetail(CommonDetail):
    model = Quadraset

class QuadrasetCreate(CommonCreate):
    model = Quadraset
    form_class = QuadrasetForm
    template_name = 'add/common.html'
    dirty = ['length']

class QuadrasetUpdate(CommonUpdate):
    model = Quadraset
    form_class = QuadrasetForm
    template_name = 'add/common.html'
    dirty = ['length']

class QuadrasetDelete(CommonDelete):
    model = Quadraset

##################
### QUEUE: add ###
def queue_add_vu(request):
    if request.method == 'POST':
        form = QueueForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/quadranym/add/conjugal')
    else:
        form = QueueForm()
    return render(request, 'add/queue.html', dict(form=form))

########## END DATABASE CRUD ##########
#######################################



#############################
########## COMPARE ##########

### APOLYSIS
def apolysis_vu(request):
    polys = orderfy(Polynym)
    url = request.POST.get('url', 'https://en.wikipedia.org/wiki/Sappho')
    poly_ids = [int(x) for x in request.POST.getlist('poly_id')] if 'poly_id' in request.POST \
                      else [p.id for p in sample(set(polys), choice(range(2, 48)))]
    nams, deps, terms, areas, sources, total, utotal = unions(poly_ids)
    return render(request, 'compare/apolysis.html',
                  dict(polys=polys, nams=nams, poly_ids=poly_ids,
                       deps=deps, terms=terms, url=url, freq=word_freq(nams, url),
                       total=total, utotal=utotal,
                       areas=areas, sources=sources, red=((total/utotal)-1)*100))
### POLYMATH
def polymath_vu(request):
    polys = orderfy(Polynym)
    p1k, p2k = [x.id for x in sample(list(polys), 2)] if not 'p1_id' in request.POST \
                or not 'p2_id' in request.POST else (request.POST['p1_id'], request.POST['p2_id'])
    p1 = Polynym.objects.get(pk=p1k)
    p2 = Polynym.objects.get(pk=p2k)
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

### POLYTILE
def polytile_vu(request):
    polys = orderfy(Polynym)
    poly = choice(polys) if not 'poly_id' in request.POST else \
               get_object_or_404(Polynym, pk=request.POST['poly_id'])
    named = request.POST.get('named', '')
    dep = poly.depth if not named == 'on' else poly.depth + 1
    wdt = 'dep' if not 'wdt' in request.POST else request.POST['wdt']
    hgt = 'dep' if not 'hgt' in request.POST else request.POST['hgt']
    rows = polytile_table(poly, int(wdt) if wdt != 'dep' else \
                           dep, int(hgt) if hgt != 'dep' else dep, bool(named == 'on'))
    return render(request, 'compare/polytile.html',
                  dict(poly=poly, polys=polys, rows=rows, dep=dep, wdt=wdt, hgt=hgt, named=named))

### QONTEXT
def qontext_vu(request):
    quads = orderfy(Quadranym)
    q1 = choice(quads) if not 'q1_id' in request.POST else get_object_or_404(Quadranym, pk=request.POST['q1_id'])
    q2 = choice(quads) if not 'q2_id' in request.POST else get_object_or_404(Quadranym, pk=request.POST['q2_id'])
    q3 = choice(quads) if not 'q3_id' in request.POST else get_object_or_404(Quadranym, pk=request.POST['q3_id'])
    return render(request, 'compare/qontext.html', dict(quads=quads, q1=q1, q2=q2, q3=q3))

### SECTIONYM
def section_vu(request):
    supr = request.POST.get('supr')
    sex = sections(thingify(Polynym), supr)
    got = [x for x in sex if x[0] == request.POST.get('ab_id')]
    abid, a, ab, b = choice(sex) if not got or not 'ab_id' in request.POST else got[0]
    a_sides = [x for x in a.nyms() if not x in ab] # nonsections
    b_sides = [x for x in b.nyms() if not x in ab]
    a_cut = len(a_sides)//2 # nonsection L/R split point
    b_cut = len(b_sides)//2
    return render(request, 'compare/section.html',
                  dict(abid=abid, abs=sex, a=a, b=b, ab=ab, supr=supr, \
                       n=a_sides[:a_cut], s=a_sides[a_cut:],
                       e=b_sides[:b_cut], w=b_sides[b_cut:]))

### UNIONYM
def union_vu(request):
    polys = orderfy(Polynym)
    poly_ids = [int(x) for x in request.POST.getlist('poly_id')] if 'poly_id' in request.POST \
            else [p.id for p in sample(set(polys), choice(range(2, 48)))]
    nams, deps, terms, areas, sources, total, utotal = unions(poly_ids)
    plen = len(poly_ids)
    drop_dim = ((total/utotal)-1)*100 # Convergence:    dimension
    drop_dep = ((plen/len(deps))-1)*100               # depth
    drop_area = ((plen/len(areas))-1)*100             # area
    drop_src = ((plen/len(sources))-1)*100            # source
    drop_top = ((plen/len(nams))-1)*100               # topic
    return render(request, 'compare/union.html',
                  dict(polys=polys, nams=nams,
                       poly_ids=poly_ids, deps=deps, terms=terms,
                       drop_dim=drop_dim, drop_dep=drop_dep,
                       drop_area=drop_area, drop_src=drop_src,
                       drop_top=drop_top, total=total, utotal=utotal,
                       areas=areas, sources=sources))

##########################
########## FIND ##########

### HYPERQ: Quadranym.name
def hyperq_vu(request, name=None):
    quads = orderfy(Quadranym)
    if name is not None:
        quad = quads.filter(name=name.replace('-', ' '))
        if not quad:
            return render(request, 'find/hyperq.html',
                          dict(quads=quads, msg='Quadranym not found!'))
        quad = quad[0]
    else:
        quad = choice(quads) if 'quad_id' not in request.POST else \
                                          get_object_or_404(Quadranym, pk=request.POST['quad_id'])
    eq = Quadranym.objects.filter(name=quad.e) | Quadranym.objects.filter(name__icontains=quad.e)
    rq = Quadranym.objects.filter(name=quad.r) | Quadranym.objects.filter(name__icontains=quad.r)
    oq = Quadranym.objects.filter(name=quad.o) | Quadranym.objects.filter(name__icontains=quad.o)
    sq = Quadranym.objects.filter(name=quad.s) | Quadranym.objects.filter(name__icontains=quad.s)
    return render(request, 'find/hyperq.html', dict(quad=quad, quads=quads,
                                                    eq=None if not eq else eq[0],
                                                    rq=None if not rq else rq[0],
                                                    oq=None if not oq else oq[0],
                                                    sq=None if not sq else sq[0]))

### QFIND: Quadranym.name
def qfind_vu(request, name=None):
    quads = orderfy(Quadranym)
    words = sorted(list(set(sum([q.nyms() for q in quads], []))))
    name = request.POST.get('word') if 'word' in request.POST else name
    if name is not None:
        word = name.replace('-', ' ')
        quad = quads.filter(Q(name=word) | Q(e=word) | Q(r=word) | Q(o=word) | Q(s=word) \
                          | Q(name=name) | Q(e=name) | Q(r=name) | Q(o=name) | Q(s=name))
        if not quad:
            return render(request, 'find/quadranym.html', dict(words=words, msg='Word not found!'))
        quad = quad[0]
    else:
        word = choice(words)
    rows, neros, got_quads = findquad_table(word, quads)
    return render(request, 'find/quadranym.html',
                  dict(word=word, words=words, rows=rows, neros=neros,
                       got_quads=got_quads, wordr=word.replace(' ', '\ ')))

### PFIND: Polynym.name
def pfind_vu(request, name=None):
    polys = orderfy(Polynym)
    words = sorted(list(set(sum([p.nyms(True) for p in polys], []))))
    name = request.POST.get('word') if 'word' in request.POST else name
    if name is not None:
        word = name.replace('-', ' ')
        poly = polys.filter(Q(name=word) | Q(p1=word) | Q(p2=word) | Q(p3=word) | Q(p4=word) | \
                            Q(p5=word) | Q(p6=word) | Q(p7=word) | Q(p8=word) | Q(p9=word) | \
                            Q(p10=word) | Q(p11=word) | Q(p12=word) | Q(name=name) | Q(p1=name) | \
                            Q(p2=name) | Q(p3=name) | Q(p4=name) | Q(p5=name) | Q(p6=name) | \
                            Q(p7=name) | Q(p8=name) | Q(p9=name) | Q(p10=name) | \
                            Q(p11=name) | Q(p12=name))
        if not poly:
            return render(request, 'find/polynym.html', dict(words=words, msg='Word not found!'))
        poly = poly[0]
    else:
        word = choice(words)
    rows, ns, got_polys = findpoly_table(word, polys)
    d = '+'.join([f'P_{ {x} }' if y != '1' else f'{ y }P_{ x }' for x, y in ns.items() if y])
    return render(request, 'find/polynym.html',
                  dict(word=word, words=words, rows=rows, ns=ns, got_polys=got_polys,
                       d=f'{d}', wordr=word.replace(' ', '\ ')))

###########################
########## GUESS ##########

### EMONYMS
def emo_vu(request):
    polys = Polynym.objects.filter(Q(name='mood') | \
                                   Q(name='moodset')).order_by('depth', 'src', 'name')
    poly = Polynym.objects.get(name='mood', src='Paul Ekman') if not 'poly_id' in request.POST \
                      else get_object_or_404(Polynym, pk=request.POST['poly_id'])
    word = request.POST.get('word', '')
    moods = {syn.split(',')[0]:syn for syn in poly.nyms()}
    emos = [(m, v, v*4, shade(v)) for m, v in guess_mood(word, moods.values()) if v > 0]
    mood = 'none' if not emos else emos[0][0] # single mood
    emo = 'none' if not emos else '/'.join(moods[mood].split(',')) # multi-mood emotion
    say = 'makes me' if poly.src == 'Paul Ekman' else 'feels' if poly.src == 'William James' \
                     else 'relates to feeling' if poly.src == '2DES' else 'feels'
    say = f'{word.capitalize()} {say} {emo}.'
    return render(request, 'guess/emo.html', dict(word=word, poly=poly, polys=polys,
                                                  emos=emos, mood=mood, say=say))

### POLYKINS
def polykins_vu(request):
    polys = orderfy(Polynym)
    poly = choice(polys) if not 'poly_id' in request.POST else \
                            get_object_or_404(Polynym, pk=request.POST['poly_id'])
    word = request.POST.get('word', '')
    moods = {syn.split(',')[0]:syn for syn in poly.nyms()}
    emos = [(m, v, v*4, shade(v)) for m, v in guess_mood(word, moods.values()) if v > 0]
    mood = 'none' if not emos else emos[0][0] # single-nym mood
    emo = 'none' if not emos else '/'.join(moods[mood].split(',')) # multi-nym emotion
    say = f'{word.capitalize()} relates to {emo}.'
    return render(request, 'guess/polykins.html', dict(word=word, poly=poly, polys=polys,
                                                       emos=emos, mood=mood, say=say))

##########################
########## PLAY ##########

### FUN/MARRY/KILL
def fmk_vu(request):
    poly = get_object_or_404(Polynym, name='~fmk')
    w1 = request.POST.get('word1', '')
    w2 = request.POST.get('word2', '')
    w3 = request.POST.get('word3', '')
    best = guess_fit((w1, w2, w3), poly.nyms()) if w1 else \
                    [('pal', 4), ('prince', 19), ('shooter', 29)]
    return render(request, 'play/fmk.html', dict(emos=[(m, v, v*4, shade(v)) for m, v in best]))

### POLYPUZZLE
def polypuzl_vu(request):
    poly = choice(orderfy(Polynym))
    was = request.POST.get('clu')
    at = int(request.POST.get('at', '0'))
    sco = int(request.POST.get('sco', '0'))
    hi = Winner.objects.filter(app='puz').order_by('-score')[0]
    nu = int(request.POST.get('nu', '0')) + 1
    if not was:
        msg = None
    elif not was == request.POST.get('guess'):
        msg = f'Sorry, it was "{was}"'
    else:
        at += sco
        msg = f'Got it! {sco} points.'
    if not '_save' in request.POST:
        return render(request, 'play/polypuzl.html',
                      dict(poly=poly, clu=choice(poly.nyms()),
                           w=(hi.score, hi.user), nu=nu, at=at, msg=msg))
    msg = f"Nice {request.user}, but you didn't beat your high score."
    won = Winner.objects.filter(user=request.user, app='puz')
    if not won or at > won[0].score:
        win = Winner(user=request.user, app='puz') if not won else won[0]
        win.round = nu
        win.score = at
        win.save()
    msg = f'Congratulations on a new high score, {request.user}!'
    hi, fx = fame('puz')
    return render(request, 'play/polyfame.html', dict(hi=hi, fx=fx, msg=msg))

def polyfame_vu(request):
    hi, fx = fame('puz')
    return render(request, 'play/polyfame.html', dict(hi=hi, fx=fx))

### QUIZZECTION
def quizzection_vu(request):
    sex = sections(thingify(Polynym))
    got = [x for x in sex if x[0] == request.POST.get('abid')]
    abid, a, ab, b = choice(sex) if not got or not 'abid' in request.POST else got[0]
    a_sides = [x for x in a.nyms() if not x in ab] # nonsections
    b_sides = [x for x in b.nyms() if not x in ab]
    a_cut = len(a_sides)//2 # nonsection split sizes
    b_cut = len(b_sides)//2
    was = request.POST.get('clu')
    at = int(request.POST.get('at', '0'))
    sco = int(request.POST.get('sco', '0'))
    hi = Winner.objects.filter(app='sec').order_by('-score')[0]
    nu = int(request.POST.get('nu', '0')) + 1
    if not was:
        msg = None
    elif not was == request.POST.get('guess'):
        msg = f'Sorry, it was "{was}"'
    else:
        at += sco
        msg = f'Got it! {sco} points.'
    if not '_save' in request.POST:
        return render(request, 'play/quizzection.html',
                      dict(a=a, b=b, abs=sex, ab=ab, abid=abid,
                           clu=choice(ab), nu=nu, at=at, wi=(hi.score, hi.user),
                           n=a_sides[:a_cut], s=a_sides[a_cut:],
                           e=b_sides[:b_cut], w=b_sides[b_cut:], msg=msg))
    msg = f"Nice {request.user}, but you didn't beat your high score."
    won = Winner.objects.filter(user=request.user, app='sec')
    if not won or at > won[0].score:
        win = Winner(user=request.user, app='sec') if not won else won[0]
        win.round = nu
        win.score = at
        win.save()
        msg = f'Congratulations on a new high score, {request.user}!'
    hi, fx = fame('sec')
    return render(request, 'play/quizfame.html', dict(hi=hi, fx=fx, msg=msg))

def quizfame_vu(request):
    hi, fx = fame('sec')
    return render(request, 'play/quizfame.html', dict(hi=hi, fx=fx))

##########################
########## TELL ##########

### TALESPIN
def fspin_vu(request): # user picks Qs for Fable!
    quads = orderfy(Quadranym)
    fabls = orderfy(Fable)
    msg, got_quads, fabl = None, None, None
    try:
        got_quads = [Quadranym.objects.get(pk=i) for i in request.POST.getlist('quad_id')]
        fabl = Fable.objects.get(pk=request.POST.get('fabl_id'))
    except (KeyError, Quadranym.DoesNotExist, Fable.DoesNotExist):
        fabl = choice(fabls) if not fabl else fabl
        got_quads = sample(list(quads), fabl.length) if not got_quads else got_quads
    rev = request.POST.get('rev')
    if rev == 'on':
        got_quads.reverse()
    msg = 'Not enough topics!' if len(got_quads) < fabl.length else msg
    msg = 'Too many topics!' if len(got_quads) > fabl.length else msg
    if not got_quads or not fabl:
        return render(request, 'tell/fspin.html',
                      dict(quads=quads, fabls=fabls, msg='Pick your Topics!'))
    return render(request, 'tell/fspin.html',
                  dict(quads=quads, fabls=fabls, spun=deqodes(got_quads, fabl.qode),
                       got_quads=got_quads, fabl=fabl, quad_ids=[q.id for q in got_quads],
                       rev=rev, trace=request.POST.get('trace'), msg=msg))

### SPINVERSE
def mspin_vu(request): # pick & spin: Phra x Quad
    path = request.POST.get('path', 'tq')
    got_quads = [Quadranym.objects.get(pk=i) for i in request.POST.getlist('quad_id')]
    got_phras = [Phrase.objects.get(pk=i) for i in request.POST.getlist('phra_id')]
    if not got_quads or not got_phras:
        return render(request, 'tell/mspin.html',
                      dict(quads=orderfy(Quadranym), phras=orderfy(Phrase),
                           quad_ids=[], phra_ids=[], path='qt'))
    return render(request, 'tell/mspin.html',
                  dict(quads=orderfy(Quadranym), phras=orderfy(Phrase),
                       spun=pairspin(got_phras, got_quads, path),
                       quad_ids=[int(q.id) for q in got_quads],
                       phra_ids=[int(ph.id) for ph in got_phras],
                       path=path, trace=request.POST.get('trace')))

### EZ-SPIN
def qspin_vu(request): # pick & spin: Phras x Quads
    quads = sample(list(thingify(Quadranym)), 15)
    phras = sample(list(thingify(Phrase)), 15)
    quad = Quadranym.objects.get(pk=request.POST.get('quad_id')) \
                    if 'quad_id' in request.POST else choice(orderfy(Quadranym))
    phra = Phrase.objects.get(pk=request.POST.get('phra_id')) \
                 if 'phra_id' in request.POST else choice(orderfy(Phrase))
    return render(request, 'tell/qspin.html',
                  dict(quads=quads, phras=phras, quad=quad, phra=phra, spun=phra.spin(quad)))

### ORAQUEUE
def oraq_vu(request): # pick & flip: Fort x Quad
    quads = orderfy(Quadranym)
    forts = orderfy(Fortune)
    msg, got_quads, fort = None, None, None
    try:
        got_quads = [Quadranym.objects.get(pk=i) for i in request.POST.getlist('quad_id')]
        fort = Fortune.objects.get(pk=request.POST.get('fort_id'))
    except (KeyError, Quadranym.DoesNotExist, Fortune.DoesNotExist):
        fort = choice(forts) if not fort else fort
        got_quads = sample(list(quads), fort.depth) if not got_quads else got_quads
    exes = [x.name for x in list(set(fort.q2.all() | fort.q1.all()))]
    trace = request.POST.get('trace')
    rev = request.POST.get('rev')
    if rev == 'on':
        got_quads.reverse()
    msg = 'Not enough topics!' if len(got_quads) < fort.depth else msg
    msg = 'Too many topics!' if len(got_quads) > fort.depth else msg
    if not got_quads:
        return render(request, 'tell/oraq.html',
                      dict(forts=forts, quads=quads, msg='Pick your destiny!'))
    return render(request, 'tell/oraq.html',
                  dict(fort=fort, forts=forts, quads=quads, spun=fort.spin_fortune(got_quads),
                       quad_ids=[q.id for q in got_quads], exes=exes,
                       rev=rev, trace=trace, msg=msg))

### UNQUOTE
def unquote_vu(request): # pick & flip: Quote x Quad
    quads = orderfy(Quadranym)
    quots = orderfy(Quote)
    try:
        quad = Quadranym.objects.get(pk=request.POST.get('quad_id'))
        quot = Quote.objects.get(pk=request.POST.get('quot_id'))
    except (KeyError, Quadranym.DoesNotExist, Quote.DoesNotExist):
        quad = choice(quads)
        quot = choice(quots)
    if not quad or not quot:
        return render(request, 'tell/unquote.html',
                      dict(quots=quots, quads=quads, msg='Pick below!'))
    return render(request, 'tell/unquote.html',
                  dict(quots=quots, quads=quads, quot=quot, quad=quad,
                       spun=quot.spin_quote(quad, True)))

### TURNR: WIP - local ok, needs spaCy on server!
def turnr_vu(request):
    q1_ids = request.POST.getlist('q1_id')
    q2_ids = request.POST.getlist('q2_id')
    quad1s = [Quadranym.objects.get(pk=i) for i in q1_ids]
    quad2s = [Quadranym.objects.get(pk=i) for i in q2_ids]
    txt = turn(request.POST.get('txt'), quad1s, quad2s)
    return render(request, 'tell/turnr.html', dict(txt=txt, quads=orderfy(Quadranym),
                                                   q1_ids=[q.pk for q in quad2s],
                                                   q2_ids=[q.pk for q in quad1s]))

#######################
##### PLOT CHARTS #####
def plot_vu(request):
    typ = request.POST.get('typ', 'area_rng')
    ob = request.POST.get('ob', 'poly')
    ob = 'poly' if typ in ('sectionym', 'mode_dist', 'area_rng', 'src_rng', 'tilemap') else ob
    ob = 'poly' if typ == 'wordcloud' and ob not in ('poly', 'quad', 'fabl', 'phra') else ob
    ob = 'quad' if typ in ('realm_dist', 'polar') else ob
    return render(request, 'compare/plot.html', {'typ': typ, 'ob': ob})
def plot_poly_area_rng(request): # DEPTHS: poly
    return depth_rng(thingify(Polynym), 'area')
def plot_poly_src_rng(request):
    return depth_rng(thingify(Polynym), 'src')
def plot_poly_mode_deps(request):
    return depth_modes(thingify(Polynym))
def plot_poly_sectionym(request): # DEPENDENCY WHEEL: poly
    return nym_wheel(sections(thingify(Polynym), thresh=1))
def plot_poly_sectionet(request): # NETWORK GRAPH: poly/quad
    return nym_graph(sections(thingify(Polynym)))
def plot_quad_sectionet(request):
    return nym_graph(sections(thingify(Quadranym)))
def plot_quad_polar(request):     # POLAR: quad
    return polar(thingify(Quadranym))
def plot_poly_wordcloud(request): # WORDCLOUD: fabl/phra/poly/quad
    return wordcloud(thingify(Polynym), 'Polynym')
def plot_quad_wordcloud(request):
    return wordcloud(thingify(Quadranym), 'Quadranym')
def plot_phra_wordcloud(request):
    return wordcloud(thingify(Phrase), 'Phrase')
def plot_fabl_wordcloud(request):
    return wordcloud(Fable.objects.all(), 'Fable')
def plot_poly_mode_dist(request): # MODE DIST PIE: poly
    return field_dist(thingify(Polynym), 'mode')
def plot_quad_realm_dist(request): # REALM DIST PIE: quad
    return field_dist(thingify(Quadranym), 'realm')
def plot_tale_area_dist(request): # AREA DIST PIE: fabl/phra/poly/pmap/quad/stry/tale
    return field_dist(Tale.objects.all(), 'area')
def plot_fabl_area_dist(request):
    return field_dist(Fable.objects.all(), 'area')
def plot_stor_area_dist(request):
    return field_dist(Story.objects.all(), 'area')
def plot_phra_area_dist(request):
    return field_dist(thingify(Phrase), 'area')
def plot_poly_area_dist(request):
    return field_dist(thingify(Polynym), 'area')
def plot_quad_area_dist(request):
    return field_dist(thingify(Quadranym), 'area')
def plot_pmap_area_dist(request):
    return field_dist(Polymap.objects.all(), 'area')
def plot_tale_src_dist(request):# SOURCE DIST PIE: fabl/phra/poly/pmap/quad/stry/tale
    return field_dist(Tale.objects.all(), 'src')
def plot_fabl_src_dist(request):
    return field_dist(Fable.objects.all(), 'src')
def plot_stor_src_dist(request):
    return field_dist(Story.objects.all(), 'src')
def plot_phra_src_dist(request):
    return field_dist(thingify(Phrase), 'src')
def plot_poly_src_dist(request):
    return field_dist(thingify(Polynym), 'src')
def plot_quad_src_dist(request):
    return field_dist(thingify(Quadranym), 'src')
def plot_pmap_src_dist(request):
    return field_dist(Polymap.objects.all(), 'src')

################
##### LIST #####
class QuadranymList(ListView):
    model = Quadranym
    template_name = 'see/quadranym_list.html'
    ordering = ['name']
class PolynymList(ListView):
    model = Polynym
    template_name = 'see/polynym_list.html'
    ordering = ['name']

################
##### SORT #####
class QuadranymTable(ListView):
    model = Quadranym
    template_name = 'see/quadranym_sort.html'
class PolynymTable(ListView):
    model = Polynym
    template_name = 'see/polynym_sort.html'


##############################
########## DISABLED ##########

# def get_context_data(self, *args, **kwargs):
#    kwargs['pk'] = self.get_object().pk
#    return super().get_context_data(**kwargs)

# class CommonWizard(SessionWizardView):
#    many = None
#    def get_template_names(self):
#        return [self.templates[int(self.steps.current)]]
#    def done(self, form_list, form_dict, **kwargs):
#        data = do_dict(form_list)
#        if self.many is not None:
#            many_things = data.pop(self.many)
#        thing = self.model(**data)
#        thing.save()
#        if self.many is not None:
#            thing.quadranyms.add(*many_things)
#            thing.save()
#        return redirect(f'/{thing.whois()}/{thing.pk}')

# class QuadrasetWizard(CommonWizard):
#    templates = ['add/wiz.html', 'add/wiz.html']
#    model = Quadraset
#    many = 'quadranyms'
#    #form_list = [QuadrasetForm1, QuadrasetForm2]
