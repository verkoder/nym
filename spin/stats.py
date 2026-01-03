#!/usr/bin/env python
# encoding: utf-8
'''
stats.py -- Nymology db & user stats
'''
from random import sample
from django.contrib.auth import get_user_model

from .cached import GAMES, badge
from .models import COMMON, Fable, Phrase, Polymap, Polynym, Quadranym, Story, Tale, Winner


def nymology_stats():
    def top(field, lim=7):
        'top values in Polynym.field'
        crop = {}
        for what, score in Polynym.data.top_field(field, lim).items():
            if not what:
                continue
            what = get_user_model().objects.get(pk=what) if not isinstance(what, str) else what
            if what not in crop:
                crop[what] = score
            else:
                crop[what] += score
        return [(y, x) for x, y in sorted(crop.items(), key=lambda kv: kv[1], reverse=True)[:lim]]
    return dict(
        top_poly=Polynym.data.samples(size=12)[1],
        pmaps=Polymap.objects.count(),
        polys=Polynym.objects.count(),
        tales=Tale.objects.count(),
        quads=Quadranym.objects.count(),
        phras=Phrase.objects.count(),
        stors=Story.objects.count(),
        fabls=Fable.objects.count(),
        areas=top('area'),
        sources=top('src'),
        wins=Winner.data.winners(),
        users=top('user'))

def playground_fun():
    return dict(
        top_stor=Story.data.picks()[1],
        top_tale=Tale.data.picks()[1],
    )

def user_stats(username):
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
    wins = {}
    total_wins = 0
    for app in GAMES.keys():
        wins[app] = Winner.data.filter(user=usr, app=app)
        total_wins += 0 if not wins[app] else wins[app][0].score
    grand = total_votes + total_nyms + total_wins
    return dict(usr=usr, usrs=sample(list(usrs.exclude(username=username)), 3),
                wins=wins, grand=grand, votes=votes.items(), nyms=nyms.items(),
                total_wins=total_wins, total_votes=total_votes, total_nyms=total_nyms,
                earn=badge(grand), msg=msg)
