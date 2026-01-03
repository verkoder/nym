#!/usr/bin/env python
# encoding: utf-8
'''
makers.py -- Nymology storymakers
'''
from django.shortcuts import get_object_or_404

from .cached import NEWLINE, NEWLINE2
from .methods import deqodes, quad_spin
from .models import Fable, Phrase, Quadranym

def paired(phras, quads):
    return '<br>'.join([f'{q} &mdash; {p}' if not p == q == '-' else '<small>&para;</small>' \
       for p, q in zip([ph.name for ph in phras], [q.name for q in quads])])

# STORYMAKERS
def story_menu(request):
    'Topic-Phrase Menu Story'
    phra_id = None if not 'phra_id' in request.POST else int(request.POST['phra_id'])
    quad_id = None if not 'quad_id' in request.POST else int(request.POST['quad_id'])
    phra_ids = [] if not 'phra_ids' in request.POST else \
                      [int(x) for x in request.POST.get('phra_ids').split(',') if x]
    quad_ids = [] if not 'quad_ids' in request.POST else \
                      [int(x) for x in request.POST.get('quad_ids').split(',') if x]
    if not '_save' in request.POST:
        if '_line' in request.POST:
            quad_ids.append(Quadranym.objects.get(name='-').pk) # TRY/ADD
            phra_ids.append(Phrase.objects.get(name='-').pk)
        elif phra_id and quad_id:
            quad_ids.append(quad_id) # TRY/ADD
            phra_ids.append(phra_id)
    phrases = [Phrase.objects.get(pk=pk) for pk in phra_ids]
    quadranyms = [Quadranym.objects.get(pk=pk) for pk in quad_ids]
    spun,qode = quad_spin(phrases, quadranyms)
    if quad_ids and '_try' in request.POST:
        for undo in (quadranyms, phrases, quad_ids, phra_ids):
            undo.pop() # REMOVE TRY-ONLY
    phra_ids = ','.join([str(x) for x in phra_ids])
    quad_ids = ','.join([str(x) for x in quad_ids])
    pairs = paired(phrases, quadranyms)
    if not '_save' in request.POST:
        return request, 'make/story_menu.html', \
               dict(spun=spun, pairs=pairs, phrases=phrases, quadranyms=quadranyms, qode=qode,
                    quads=Quadranym.data.all(), quad_id=quad_id, phra_id=phra_id, length=len(phrases),
                    phras=Phrase.data.all(), quad_ids=quad_ids, phra_ids=phra_ids) # TRY/ADD
    return request, 'make/story_save.html', \
           dict(spun=spun, length=len(phrases), pairs=pairs, qode=qode, quad_ids=quad_ids, phra_ids=phra_ids) # NEXT

def story_pair(request):
    'Topic-Phrase Pair Story'
    msg = None
    text = request.POST.get('pair_text', '').strip()
    _text = [x.split(',') for x in NEWLINE.split(NEWLINE2.sub('\n-,-\n', text)) if ',' in x]
    quad_names, phra_names = [x[0] for x in _text], [x[1] for x in _text]
    quadranyms = [q[0] for q in [Quadranym.objects.filter(name=n) for n in quad_names] if q]
    phrases = [ph[0] for ph in [Phrase.objects.filter(name=n) for n in phra_names] if ph]
    spun,qode = quad_spin(phrases, quadranyms)
    pairs = paired(phrases, quadranyms)
    if len(quadranyms) != len(quad_names) or len(phrases) != len(phra_names):
        msg = ', '.join([x for x in [quad_names[i] if len(q) == 0 else \
          None for i, q in enumerate([Quadranym.objects.filter(name=n) \
               for n in quad_names])] if x is not None] \
          + [x for x in [phra_names[i] if len(ph) == 0 else \
          None for i, ph in enumerate([Phrase.objects.filter(name=n) \
               for n in phra_names])] if x is not None])
        msg = f"Oops! Can't find [{msg}]"
    if not '_save' in request.POST:
        return request, 'make/story_pair.html', \
               dict(spun=spun, pairs=pairs, pair_text=text, length=len(phrases),
                    quads=Quadranym.data.all(), quadranyms=quadranyms, qode=qode,
                    phras=Phrase.data.all(), phrases=phrases, msg=msg) # TELL
    return request, 'make/story_save.html', \
           dict(spun=spun, length=len(phrases), pairs=pairs, qode=qode,
                quad_ids=','.join([str(q.pk) for q in quadranyms]),
                phra_ids=','.join([str(ph.pk) for ph in phrases])) # NEXT

def story_list(request):
    'Dual Topic/Phrase Lists Story'
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
    quadranyms = [quad_dict.get(name) for name in quad_names if name]
    phrases = [phra_dict.get(name) for name in phra_names if name]
    if quadranyms and phrases and None in quadranyms or None in phrases:
        msg = ', '.join([x for x in [quad_names[i] if not q else None \
                           for i, q in enumerate(quadranyms)] if x is not None] \
                      + [x for x in [phra_names[i] if not ph else None \
                           for i, ph in enumerate(phrases)] if x is not None])
        msg = f"Oops! Can't find [{msg}]"
        phrases = [x for x in phrases if x] # patch user error
        quadranyms = [x for x in quadranyms if x]
    pairs = paired(phrases, quadranyms)
    try:
        spun,qode = quad_spin(phrases, quadranyms)
    except IndexError:
        return request, 'make/story_list.html', \
               dict(spun='', quad_txt=quad_txt, phra_txt=phra_txt, length=len(phrases),
                    quads=Quadranym.data.all(), pairs=pairs, qode='',
                    phras=Phrase.data.all(),
                    msg='Mismatched lists!') # ERROR
    if not '_save' in request.POST:
        return request, 'make/story_list.html', \
               dict(spun=spun, quad_txt=quad_txt, phra_txt=phra_txt, length=len(phrases),
                    quads=Quadranym.data.all(), pairs=pairs, qode=qode,
                    phras=Phrase.data.all(),
                    msg=msg, phrases=phrases, quadranyms=quadranyms) # TRY
    return request, 'make/story_save.html', \
           dict(spun=spun, length=len(phrases), pairs=pairs, qode=qode,
                quad_ids=','.join([str(q.pk) for q in quadranyms]),
                phra_ids=','.join([str(ph.pk) for ph in phrases])) # NEXT

# TALEMAKERS
def tale_menu(request):
    'Topic Menu Tale'
    fabl = get_object_or_404(Fable, pk=request.POST['fabl_id'])
    quad_id = None if not 'quad_id' in request.POST else int(request.POST['quad_id'])
    quad_ids = [] if not 'quad_ids' in request.POST else \
                      [int(x) for x in request.POST.get('quad_ids').split(',') if x]
    if quad_id and not '_save' in request.POST:
        quad_ids.append(quad_id)
    tale_dict = {q.pk:q for q in Quadranym.objects.filter(pk__in=quad_ids)}
    tale_quads = [tale_dict[qid] for qid in quad_ids] # avoid hitting db for each
    spun = deqodes(tale_quads, fabl.qode)
    tops = [q.name for q in tale_quads]
    if quad_ids and '_try' in request.POST:
        tops.pop()
        quad_ids.pop()
    togo = fabl.length - len(quad_ids)
    msg = f'Add {togo} topics!' if togo != 1 else 'Add last topic!'
    quad_ids = ','.join([str(x) for x in quad_ids])
    if togo != 0:
        return request, 'make/tale_menu.html', \
               dict(spun=spun, quads=Quadranym.data.all(),
                    tale_quads=tale_quads, tops=tops, fabl=fabl,
                    quad_id=quad_id, msg=msg,
                    quad_ids=quad_ids)
    #spun = spun[-1][0] if isinstance(spun[0], tuple) else spun # omit trace
    return request, 'make/tale_save.html', \
           dict(spun=spun, quad_ids=quad_ids, fabl=fabl,
                d_src=fabl.src, d_area=fabl.area, d_url=fabl.wiki, quad_txt=', '.join(tops))

def tale_list(request):
    'Topic List Tale'
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
    msg += 'Need more topics!' if len(tale_quads) < fabl.length else 'Too many topics!' \
                                if len(tale_quads) > fabl.length else None if not quad_txt else msg
    spun = None if not quad_txt else deqodes(tale_quads, fabl.qode)
    if not '_save' in request.POST:
        return request, 'make/tale_list.html', \
               dict(spun=spun, quads=Quadranym.data.all(),
                    tale_quads=tale_quads, fabl=fabl,
                    quad_txt=quad_txt, msg=msg)
    quad_ids = ','.join([str(q.pk) for q in tale_quads])
    #spun = spun[-1][0] if isinstance(spun[0], tuple) else spun # omit trace
    return request, 'make/tale_save.html', \
           dict(spun=spun, quad_ids=quad_ids, fabl=fabl, d_src=fabl.src,
                d_area=fabl.area, d_url=fabl.wiki, quad_txt=quad_txt)
