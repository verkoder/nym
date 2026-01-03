#!/usr/bin/env python
# encoding: utf-8
'''
games.py -- Nymology game template
'''
from time import time
from random import choice
from django.shortcuts import render

from .cached import GAMES
from .concept import relatedness
from .models import Winner

def fame(app, msg=None):
    'high scoring users, scores and average points-per-round'
    hi = Winner.data.filter(app=app).order_by('-score')
    fx = {x.user.username:x.score/float(x.round) for x in hi}
    fx = [(f'{y:.2f}', x) for x, y in sorted(fx.items(), key=lambda kv: kv[1], reverse=True)[:10]]
    hi = [(x.score, x.user.username) for x in hi[:10]]
    return dict(hi=hi, fx=fx, app=app, color=GAMES[app], games=GAMES.items(), msg=msg)

def quiz(request, app, attrs):
    'score a quiz-style game'
    hi = Winner.data.filter(app=app).order_by('-score')[0]
    attrs['winner'] = (hi.score, hi.user)
    attrs['app'] = app
    attrs['color'] = GAMES[app]
    attrs['tic'] = float(request.POST.get('tic', 0))
    attrs['at'] = int(request.POST.get('at', '0'))
    attrs['nu'] = int(request.POST.get('nu', '0')) + 1
    guess = request.POST.get('guess')
    was = request.POST.get('clue')
    sco = int(request.POST.get('sco', '0'))

    if not was:
        msg = None
    elif not was == guess:
        if app not in ('TheGist', 'unQuote') and \
               relatedness(was, guess) > 0.3: # close enough for partial credit
            sco = sco // 2
            msg = f'{yo(part=True)}&mdash;you had <i>{guess}</i>, it was <i>{was}</i>' \
                  f'<br>Partial credit, {sco} point{"s" if sco > 1 else ""}'
            attrs['at'] += sco
        elif not guess:
            msg = f'It was <i>{was}</i>'
        else:
            msg = f'{yo(False)}&mdash;you had <i>{guess}</i>, it was <i>{was}</i>'
    else:
        msg = f'Got it! {sco} points.'
        if 'tic' in attrs:
            if time() - attrs['tic'] < 15: # under 15 seconds: +10 points
                sco += 10
                msg = f'{yo(punc=True)} Super speed bonus!!!<br>{sco} points'
            elif time() - attrs['tic'] < 30: # under 30 seconds: +5 points
                sco += 5
                msg = f'{yo(punc=True)} Speed bonus!<br>{sco} points'
        attrs['at'] += sco

    if not '_save' in request.POST:
        attrs['msg'] = msg
        attrs['tic'] = time()
        return render(request, f'play/{app.lower()}.html', attrs)

    won = Winner.data.filter(user=request.user, app=app)
    if not won or attrs['at'] > won[0].score:
        win = Winner(user=request.user, app=app) if not won else won[0]
        win.round = attrs['nu']
        win.score = attrs['at']
        win.save()
        msg = f'Your finest hour, {request.user}!'
    elif attrs['at'] == won[0].score:
        msg = f'Great {request.user}, you tied your best score!'
    else:
        msg = f'Nice {request.user}, but {won[0].score - attrs["at"]} points from your best.'

    return render(request, 'play/fame.html', fame(app, msg))

def yo(yes=True, punc=False, part=False):
    'humanized boolean-ish response'
    if part:
        return choice(('Almost', 'Close enough for jazz', 'Good enough', 'In a way',
                       "I'll give it to ya", 'Kind of', 'More or less', 'Partly',
                       'Sort of', 'Well', 'You get the idea', "You're almost there"))
    out = choice(('Nice try', 'No', 'Nope', 'Not exactly', 'Not quite', 'Oh well',
                  'Oops', 'Sadly', 'Sorry', "That's not it", 'Try again',
                  'Unfortunately', 'Valiant effort')) if not yes \
     else choice(('Awesome','Exactly', 'Correct', 'Excellent', 'Good job', 'Got it',
                  'Great', 'Indeed', 'Nice', 'Nailed it', "Oh, you're good", 'Okay',
                  'Very good', 'Well done', 'Yes', 'You guessed it', 'Yup'))
    return out if not punc else out + choice(('!', '.'))
