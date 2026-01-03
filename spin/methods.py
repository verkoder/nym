#!/usr/bin/env python
# encoding: utf-8
'''
methods.py -- Nymology general data methods
'''
import urllib
import urllib3
from .cached import GRAYS, WIKI

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
HTTP = urllib3.PoolManager()


def deqodes(q_list, text):
    'deqode via Quadranym list: FIFO'
    for i, q in enumerate(q_list, 1):
        text = q.deqode(text, i)
    return text

def poly_tile(p, wdt, hgt, named):
    'Polynym tile table'
    dep = p.depth if not named else p.depth + 1
    row = list(zip(p.nyms(named), GRAYS[:dep])) * 37
    return [row[i:wdt+i] for i in list(range(hgt))]

def polyset_table(polys):
    'Polyset view table'
    depth = max([p.depth for p in polys])
    width = sum([p.depth for p in polys])
    tabl = [[p, p.p1, p.p2, p.p3, p.p4, p.p5, p.p6, p.p7, p.p8,
             p.p9, p.p10, p.p11, p.p12][:depth+1] for p in polys]
    return depth, width, tabl, list(range(depth))

def quad_spin(phras, quads, path=None, qode=False):
    'spin text from Quadranyms and Phrases via path, zip by default, return spun,qode'
    spun = []
    qode = []
    if path == 'qt': # Phrase-spin
        for i, quad in enumerate(quads):
            for phra in phras:
                spun.append(phra.spin(quad)+'<br>' if quad.name !='-' else '<br>')
                qode.append(phra.qode+'<br>' if quad.name !='-' else '<br>')
            spun.append('<br>')
            qode.append('<br>')
    elif path == 'tq': # Topic-spin
        for i, phra in enumerate(phras):
            for quad in quads:
                spun.append(phra.spin(quad)+'<br>' if quad.name !='-' else '<br>')
                qode.append(phra.qode+'<br>' if quad.name !='-' else '<br>')
            spun.append('<br>')
            qode.append('<br>')
    else: # Zipper
        lim = min(len(quads)-1, len(phras)-1) + 1
        for i in range(lim):
            quad = quads[i]
            phra = phras[i]
            spun.append(phra.spin(quad)+'<br>' if quad.name !='-' else '<br>')
            qode.append(phra.qode+'<br>' if quad.name !='-' else '<br>')
    return ' '.join(spun) if not qode else ' '.join(spun), ' '.join(qode)

def quad_turn(text, q1s, q2s):
    'turn enqode/deqode by dual Quadranym lists'
    if not text:
        return ''
    for i, quad in enumerate(q1s):
        text = quad.enqode(text, i)
    for i, quad in enumerate(q2s):
        text = quad.deqode(text, i)
    return text

def wikify(url):
    'style wikipedia URL'
    wiki = WIKI.search(url)
    return url[:18]+'...' if not wiki else urllib.parse.unquote(
        '<img src="/static/spin/img/wikipedia-icon16.png"> '
        f'{wiki.group(2)}').replace('_', ' ')

def word_freq(words, url):
    'word frequencies in URL with max=200'
    if not url.startswith('https://en.wikipedia.org/'):
        return 'Enter wikipedia URL', []
    try:
        r = HTTP.request('GET', url)
    except urllib3.exceptions.LocationValueError:
        return 'Enter a wikipedia URL', []
    html = r.data
    if not html:
        return []
    freq = {}
    for word in words:
        total = html.count(word.encode('utf-8'))
        if total:
            freq[word] = total
    return None, sorted(freq.items(), key=lambda kv: kv[1], reverse=True)
