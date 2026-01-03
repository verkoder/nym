#!/usr/bin/env python
# encoding: utf-8
'''
managers.py -- Nymology data managers
'''
from functools import reduce
from itertools import combinations
from operator import itemgetter, or_
from random import choice, sample
from django.db import models
from django.db.models.functions import Lower
from django.db.models import Q

from .cached import GRAYS

# GENERAL MANAGERS
class Picker(models.Manager):
    '''Model.data.picks()       [all Common models]
       Model.data.top_field()
    '''
    class Meta:
        abstract = True

    def get_queryset(self):
        return super().get_queryset().order_by(Lower('name'))

    def picks(self, request=None, attr='pk', pk=None):
        'get item from request[attr] or choice'
        things = self.all()
        if pk is not None:
            try:
                return things, things.get(pk=pk)
            except self.model.DoesNotExist:
                return things, choice(things)
        try:
            return things, things.get(pk=request.POST[attr])
        except (KeyError, AttributeError, self.model.DoesNotExist):
            return things, choice(things)

    def top_field(self, field='user', lim=7, sort=False):
        'top values in Common object.field'
        out = self.values_list(field).annotate(ord=models.Count(field)).order_by('-ord')
        out = dict([(k, v) for k, v in out if k][:lim])
        if not sort:
            return out
        return sorted(out.items(), key=lambda kv: kv[1], reverse=True)

class Sampler(Picker):
    '''Model.data.samples()     [Phrase, Polynym, Quadranym]
       Model.data.sections()
    '''
    class Meta:
        abstract = True

    def samples(self, request=None, attr='pk', size=None, rev=None):
        'getlist from request[attr] or sample -- Phrase/Polynym/Quadranym'
        msg = None
        things = list(self.all())
        if request is not None and attr in request.POST:
            thing_ids = [int(x) for x in request.POST.getlist(attr)]
            spin_things = [x for x in things if x.id in thing_ids]
            if size is not None:
                msg = 'Not enough topics!' if len(spin_things) < size else msg
                msg = 'Too many topics!' if len(spin_things) > size else msg
        else:
            spin_things = sample(things, size if size is not None else choice((5, 10, 15, 20)))
            thing_ids = [p.pk for p in spin_things]
        if rev == 'on':
            spin_things.reverse()
        return things, spin_things, thing_ids, msg

    def sections(self, supernyms=False, thresh=0):
        'mine for intersections; optional supernyms=True or codimensions > thresh'
        sex = []
        used = {x.id:0 for x in self.all()}
        nyms = {x.id:set(x.nyms(named=False)) for x in self.all()} # dimension dict
        comb = [(a, b, ab) for a, b, ab in [
                (a, b, tuple(nyms[a.id].intersection(nyms[b.id]))) for a, b in combinations(self.all(), 2)] if ab]
        nyms = {k:len(v)-1 for k, v in nyms.items()}
        comb = [(a, b, ab) for a, b, ab in comb if len(ab) != nyms[a.id] and len(ab) != nyms[b.id]] if not supernyms else \
               [(a, b, ab) for a, b, ab in comb if len(ab) == nyms[a.id] or len(ab) == nyms[b.id]]
        for a, b, ab in comb:
            sex.append((f'{a.id}_{b.id}', a, ab, b))
            used[a.id] += 1
            used[b.id] += 1
        return [(x, a, ab, b) for x, a, ab, b in sex if used[a.id] > thresh and used[b.id] > thresh]

# MODEL MANAGERS Fable/Poly/Quad/Polyset/Quote/Fortune
class FortuneData(Picker):
    def get_queryset(self):
        return super().get_queryset().exclude(q2=None) \
                                     .order_by(Lower('body'))

class PhraseData(Sampler):
    def get_queryset(self):
        return super().get_queryset().exclude(name='-') \
                                     .order_by(Lower('name'))

class PolynymData(Sampler):
    def get_queryset(self):
        return super().get_queryset().exclude(name__in=['~fmk', 'moodset']) \
                                     .order_by(Lower('name'))
        #return super().get_queryset().exclude(name='~fmk') \ # stops links in feel_mood from failing

    def matched_pair(self):
        'pk of two matched-depths Polynyms'
        data = {x:[] for x in range(2, 13)}
        for poly in self.all():
            data[poly.depth].append(poly)
        data = {x:y for x, y in data.items() if len(y) > 1} # at least 2 per P
        poly1, poly2 = sample(choice(list(data.values())), 2)
        return poly1.pk, poly2.pk

    def systems(self, area=None, depth=None, src=None):
        'Polynym systems by area/depth/src'
        polys = self.filter(area__icontains=area) if area is not None and area != 'all' else \
                self.filter(depth=depth) if depth is not None and depth != 1 else \
                self.filter(src__icontains=src) if src is not None and src != 'all' else \
                self.all()
        data = {poly: [] for poly in range(2, 13)}
        for poly in polys:
            data[poly.depth].append(poly)
        data = sorted(data.items())
        return polys, [x for x, y in data], [y for x, y in data]

    def unions(self, pids):
        'mine Polynyms for unions'
        polynyms = self.filter(pk__in=pids)
        terms = {}
        deps = {}
        nams = {}
        areas = {}
        sources = {}
        for p in polynyms:
            if p.name not in nams:          # NAME
                nams[p.name] = 1
            else:
                nams[p.name] += 1
            if p.depth not in deps:         # DEPTH
                deps[p.depth] = 1
            else:
                deps[p.depth] += 1
            if p.area:
                if p.area not in areas:         # AREA (optional)
                    areas[p.area] = 1
                else:
                    areas[p.area] += 1
            if p.src:
                if p.src not in sources:        # SRC (optional)
                    sources[p.src] = 1
                else:
                    sources[p.src] += 1
            for i in range(1, 13):      # P1 - P12
                word = getattr(p, f'p{i}').lower()
                if word in terms:
                    terms[word] += 1
                elif word:
                    terms[word] = 1
        return [f'{k}<sub>{v}</sub>' if v > 1 else str(k) for k, v in sorted(nams.items())], \
               [f'{k}<sub>{v}</sub>' if v > 1 else str(k) for k, v in sorted(deps.items())], \
               [f'{k}<sub>{v}</sub>' if v > 1 else k for k, v in sorted(terms.items())],     \
               [f'{k}<sub>{v}</sub>' if v > 1 else k for k, v in sorted(areas.items())],     \
               [f'{k}<sub>{v}</sub>' if v > 1 else k for k, v in sorted(sources.items())],   \
                sum([p.depth for p in polynyms]), len(terms)

    def related(self, nodes, url):
        'Polynyms containing nodes/fragments or matching URL'
        qry = reduce(or_, (Q(name__icontains=x) |
            Q(p1__icontains=x) | Q(p2__icontains=x) |
            Q(p3__icontains=x) | Q(p4__icontains=x) |
            Q(p5__icontains=x) | Q(p6__icontains=x) |
            Q(p7__icontains=x) | Q(p8__icontains=x) |
            Q(p9__icontains=x) | Q(p10__icontains=x) |
            Q(p11__icontains=x) | Q(p12__icontains=x) for x in nodes))
        return self.filter(qry | Q(wiki=url))

    def view_table(self, word):
        'nym-search view table'
        rows = []
        polynyms = []
        got = {x:[] for x in range(1, 13)} # dim:polys w/ word
        ref = list(range(0, 13)) # depth reference
        for poly in self.all():
            if word in poly.nyms(True):
                got[poly.depth].append(poly)
        got = [(k,v) for k,v in got.items() if v]
        for _dim, polys in got:
            for poly in polys: # long row for sliding..
                row = list(zip(poly.nyms(True), ref[:poly.depth+1], GRAYS[:poly.depth+1])) * 12
                for slide in range(6, 18): # outlined 6th cell
                    if row[slide][0] == word:
                        polynyms.append(poly)
                        rows.append(row[slide - 6:][:13])
                        break
        return rows, {k: len(v) for k,v in got}, polynyms

class QuadranymData(Sampler):
    def get_queryset(self):
        return super().get_queryset().exclude(name__in=['-', '--']) \
                                     .order_by(Lower('name'))

    def place_nodes(self, nodes):
        'guess EROS-placement of 4 unsorted nodes'
        out = dict(e=None, r=None, o=None, s=None)
        qs = self.all()
        qs = dict(e=[x.e for x in qs],
                  r=[x.r for x in qs],
                  o=[x.o for x in qs],
                  s=[x.s for x in qs])
        sco = {x: {eros: terms.count(x) for eros,terms in qs.items()} for x in nodes}
        sco = sorted([
            (x, sorted(y.items(), key=itemgetter(1), reverse=True)) for x,y in sco.items()
        ], key=itemgetter(0, 1), reverse=True)
        for word,li in sco:
            for eros,_ in li:
                if out[eros] is None:
                    out[eros] = word
                    break
        return out, sco

    def suggest(self, queue_class):
        return sorted(list({x.name for x in self.all()} \
                         & {x.name for x in queue_class.data.all()})) # completed

    def related(self, nodes, url):
        'Polynyms containing nodes/fragments or matching URL'
        qry = reduce(or_, (Q(name__icontains=x) |
            Q(e__icontains=x) | Q(o__icontains=x) |
            Q(s__icontains=x) | Q(r__icontains=x) for x in nodes))
        return self.filter(qry | Q(wiki=url))

    def view_table(self, word):
        'NEROS-search view table'
        got = {}
        slide = 0
        rows = []
        quadranyms = []
        ref = dict(name=0, e=1, r=2, o=3, s=4)
        neros = dict(name=0, e=0, r=0, o=0, s=0)
        for q in self.all():
            nyms = {q.name:'name', q.e:'e', q.r:'r', q.o:'o', q.s:'s'}
            if word in nyms:
                quadrant = nyms[word]
                neros[quadrant] += 1
                if not quadrant in got:
                    got[quadrant] = [q]
                else:
                    got[quadrant].append(q)
        for quadrant in neros:
            if not quadrant in got:
                continue
            quads = got[quadrant]
            quadranyms.extend(quads)
            slide = ref[quadrant]
            for q in quads:
                q15 = (
                    (q.name, 'n', 'DFDFDF'), (q.e, 'e', 'CFCFCF'), (q.r, 'r', 'BFBFBF'), (q.o, 'o', 'AFAFAF'), (q.s, 's', '9F9F9F'),
                    (q.name, 'n', '000000'), (q.e, 'e', '3F3F3F'), (q.r, 'r', '2F2F2F'), (q.o, 'o', '3F3F3F'), (q.s, 's', '2F2F2F'),
                    (q.name, 'n', '9F9F9F'), (q.e, 'e', 'AFAFAF'), (q.r, 'r', 'BFBFBF'), (q.o, 'o', 'CFCFCF'), (q.s, 's', 'EFEFEF'),
                )
                rows.append(q15[slide:] + q15[:slide])
        return rows, neros, quadranyms

class QueueData(Picker):
    def suggest(self, quad_class):
        return sorted(list({x.name for x in self.exclude(name__in=[
                            x.name for x in quad_class.data.all()])}))

class QuoteData(Picker):
    def get_queryset(self):
        return super().get_queryset().order_by(Lower('src'))

class WinnerData(models.Manager):
    def winners(self):
        wins = self.all()
        user_dict = {win.user:0 for win in wins}
        for win in wins:
            user_dict[win.user] += win.score
        return [(y, x) for x, y in sorted(user_dict.items(), key=lambda kv: kv[1], reverse=True)]
