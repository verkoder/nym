#!/usr/bin/env python
# encoding: utf-8
'''
do_charts.py -- Nymology Highcharts plotting tools
'''
from math import sqrt
from collections import Counter
from django.http import JsonResponse

AREA = {
    'Anatomy': 'Medicine',
    'Archaeology': 'Anthropology',
    'Artificial Intelligence': 'AI',
    'cognitive science': 'Cognition',
    ' ': '???',
    '': '???'
} # keys subbed by values

def polar(quadranyms):
    'radial distribution for Quadranym objects'

    # word count
    lens = len(quadranyms)
    rms = {x.realm:0 for x in quadranyms}
    relms = rms.keys()
    for realm in relms:
        d = [lens - len({getattr(q, el) for q in [q for q in quadranyms if q.realm == realm]}) for el in ('o', 'r', 's', 'e')]
        if not d[0] == d[1] == d[2] == d[3]:
            rms[realm] = d
    data = [dict(type='area', name=r, data=d, pointPlacement='between') for r, d in rms.items() if d]

    # make chart
    chart = {
        'chart':     {'polar': True},
        'title':      {'text': f'Quadranym Polar Bias'},
        'subtitle': {'text': 'Radial Term Convergence Skew'},
        'pane': {'startAngle': 0,
                 'endAngle': 360},
        'labels': {
            'items': [{
                'html': '<b>Objective</b>',
                'style': {
                    'left': '735px',
                    'top': '65px'}}, {
                    'html': '<b>Subjective</b>',
                'style': {
                    'left': '380px',
                    'top': '430px'}}, {
                'html': '<b>Expansion</b>',
                'style': {
                    'left': '380px',
                    'top': '65px'}},{
                'html': '<b>Reduction</b>',
                'style': {
                    'left': '735px',
                    'top': '430px'}}]},
        'xAxis': {'min':0, 'max': 360, 'tickInterval': 45},
        'yAxis': {'min': 0},
        'plotOptions': {
            'series': {
                'pointStart': 45,
                'pointInterval': 90},
            'column': {
                'pointPadding': 0,
                'groupPadding': 0}},
        'series': data,
        'credits': {'enabled': False}}
    return JsonResponse(chart)

def wordcloud(common, who):
    'wordcloud distribution among Common objects'

    # word count
    words = [w for p in common for w in p.nyms(True)]
    data = [dict(name=n, weight=w) for n, w in Counter(words).items()]

    # make chart
    chart = {
        'title': {'text': f'{who} word cloud'},
        'series': [{'type': 'wordcloud',
                    'data': data,
                    'name': who,
                    'size': '95%'}],
        'credits': {'enabled': False}}
    return JsonResponse(chart)

def nym_graph(sex):
    'Sectionym network graph'

    # collect sectionym relationships
    data = set()
    for abid, a, rels, b in sex:
        for rel in rels:
            data.add((a.name, rel))
            data.add((b.name, rel))
    data = [list(x) for x in data]

    # make chart
    chart = {
        'chart': {'type': 'networkgraph'},
        'title': {'text': 'Sectionym Relationships'},
        'subtitle': {'text': 'Network Graph', 'height': '100%'},
        'series': [{'name': 'Sectionym',
                    'data': data,
                    'dataLabels': {'enabled': True},
                    'size': '95%'}],
        'credits': {'enabled': False}}
    return JsonResponse(chart)

def nym_wheel(sex):
    'Sectionym dependency wheel'

    # collect sectionym ties
    data = [[a.name, b.name, 2] for ids, a, n, b in sex]

    # make chart
    chart = {
        'title': {'text': 'Sectionym Relationships'},
        'subtitle': {'text': 'Dependency Wheel'},
        'series': [{'name': 'Sectionym',
                    'keys': ['from', 'to', 'weight'],
                    'data': data,
                    'type': 'dependencywheel',
                    'dataLabels': {
                        'color': '#333',
                        'textPath': {
                            'enabled': True,
                            'attributes': {
                                'dy': 5}},
                        'distance': 10},
                    'size': '95%'}],
        'credits': {'enabled': False}}
    return JsonResponse(chart)

def field_dist(commons, atr):
    'atr distribution of Common objects'

    # word count, sort
    data = Counter([AREA.get(x, x) for x in [getattr(x, atr, '???') for x in commons]])
    data = sorted(data.items(), key=lambda x: x[1], reverse=True)

    # make chart
    who = commons[0].whois().capitalize()
    atr = atr if not atr == 'src' else 'source'
    chart = {
        'chart': {'type': 'pie'},
        'title': {'text': f'{atr.title()} Distribution: {len(commons)} {who}s'},
        'subtitle': {'text': f'{len(data)} {atr}s'},
        'series': [{'name': 'Total Area',
                    'data': data}],}
        #'credits': {'enabled': False}}
    return JsonResponse(chart)

def depth_rng(commons, atr):
    'depth range & average by attribute of Common objects'

    # calculate ranges: fos={atr: (min,max,[]), ...}
    data = {AREA.get(x, x):y for x, y in [(getattr(x, atr, '???'), [12, 0, []]) for x in commons]}
    for x in commons:
        ar = getattr(x, atr, '???')
        ar = AREA.get(ar, ar)
        lo, hi, av = data[ar]
        if x.depth < lo:
            data[ar][0] = x.depth # min
        if x.depth > hi:
            data[ar][1] = x.depth # max
        data[ar][2].append(x.depth)

    # calculate averages, sort & separate data
    data = {k:(i, o, sum(li)/len(li)) for k, (i, o, li) in data.items()}
    data = sorted(data.items(), key=lambda x: x[1][2]) # asc avg
    avg = [avg for k, (i, o, avg) in data]
    fos = [k for k, (i, o, avg) in data]
    data = [(i, o) for k, (i, o, avg) in data]

    # make chart
    who = commons[0].whois().capitalize()
    atr = atr if not atr == 'src' else 'source'
    chart = {
        'chart': {'type': 'columnrange',
                  'inverted': True},
        'title': {'text': f'{who} Depths by {atr.title()}'},
        'plotOptions': {'series': {'minPointLength': 12}},
        'xAxis': {'categories': fos,
                  'title': {'text': f'{who} {atr}'}},
        'yAxis': {'title': {'text': f'{who} depth'},
                  'floor': 2,
                  'ceiling': 12,
                  'tickAmount': 11},
        'series': [{#'type': 'columnr',
                    'name': 'Depth Range',
                    'data': data},
                    {'type': 'line',
                     'name': 'Average Depth',
                     'data': avg}],
        'credits': {'enabled': False}
    }
    return JsonResponse(chart)

def depth_modes(commons):
    'total depths by mode'

    # calc depths
    data = dict(part={x:0 for x in range(13)},
                step={x:0 for x in range(13)},
                type={x:0 for x in range(13)})
    for common in commons:
        if common.mode:
            data[common.mode][common.depth] += 1
    data = {mo:list(deps.values()) for mo, deps in data.items()}

    # make chart
    who = commons[0].whois().capitalize()
    chart = {
        'chart': {'type': 'column'},
        'title': {'text': f'Total {who} Depths by Mode'},
        'plotOptions': {'series': {'minPointLength': 12},
                        'column': {'stacking': 'normal'}},
        'yAxis': {'title': {'text': f'{who} count'}},
        'xAxis': {'title': {'text': f'{who} depth'},
                  'floor': 2,
                  'ceiling': 12,
                  'tickAmount': 11},
        'series': [{'name': 'Part',
                    'data': data.get('part', []), 'color': 'lightblue'},
                   {'name': 'Step',
                    'data': data.get('step', []), 'color': 'peru'},
                    {'name': 'Type',
                     'data': data.get('type', []), 'color': 'darkseagreen'}],
        'credits': {'enabled': False}
    }
    return JsonResponse(chart)
### WIP
def tilemap(commons):
    'WIP__SHIT SHOW: tilemap for Common objects (with depth field)'

    stuf = dict(part={x:[] for x in range(2, 13)},
                step={x:[] for x in range(2, 13)},
                type={x:[] for x in range(2, 13)})
    for common in commons:
        if common.mode:
            stuf[common.mode][common.depth].append(common)
    stuf = {mo:[y for x in list(deps.values()) for y in x] for mo, deps in stuf.items()}

    box = dict(part={}, step={}, type={})
    for mo, li in stuf.items():
        lens = len(li)
        side = sqrt(lens) // 1
        remains = int(lens - side ** 2)
        i = remains // 2
        box[mo] = dict(side=int(side), i=i, o=remains-i)
    xlen = sum([x['side'] for x in box.values()])
    ylen = xlen + sum([1 for x in box.values() if x['i']]) + sum([1 for x in box.values() if x['o']])
    xs = list(range(xlen))
    ys = list(range(ylen))
    ystep = box['step']['side'] + 1 if box['step']['i'] else 0 + 1 if box['step']['o'] else 0
    ytype = box['type']['side'] + 1 if box['type']['i'] else 0 + 1 if box['type']['o'] else 0
    yrang = (ylen - 2 - ystep - ytype, ylen - ystep - 1)
    cats = ['part' if y <= yrang[0] else 'type' if y <= yrang[1] else 'step' for y in range(ylen)]
    xs.reverse()
    ys.reverse()

    data = []
    for x in xs:
        for y in ys:
            mo = 'part' if y <= yrang[0] else 'type' if y <= yrang[1] else 'step'
            try:
                it = stuf[mo].pop(0)
                name = f'{it.depth} {it.mode}s of {it.name} ({it.src})' if it.src else f'{it.depth} {it.mode}s of {it.name}'
                data.append({'name': name, 'x': xlen-x, 'y': ylen-y, 'value': it.depth, 'hc-a2': f'P{it.depth}'})
            except:
                pass

    # make chart
    chart = {
        'chart': {'type': 'tilemap', 'height': '45%'},
        'title': {'text': 'Polynymic Table'},
        'xAxis': {'visible': True, 'categories': cats},
        'yAxis': {'visible': False},
        'colorAxis': {
            'dataClasses': [
                           {'to': 2, 'color': 'grey', 'name': '2'},
                {'from': 3, 'to': 3, 'color': 'blue', 'name': '3'},
                {'from': 4, 'to': 4, 'color': 'green', 'name': '4'},
                {'from': 5, 'to': 5, 'color': 'dodgerblue', 'name': '5'},
                {'from': 6, 'to': 6, 'color': 'lime', 'name': '6'},
                {'from': 7, 'to': 7, 'color': 'cyan', 'name': '7'},
                {'from': 8, 'to': 8, 'color': 'orange', 'name': '8'},
                {'from': 9, 'to': 9, 'color': 'violet', 'name': '9'},
                {'from': 10,'to': 10, 'color': 'red', 'name': '10'},
                {'from': 11,'to': 11, 'color': 'magenta', 'name': '11'},
                {'from': 12, 'color': 'yellow', 'name': '12'},
                ]
            },
        'series': [{'dataLabels': {
                        'enabled': True,
                        'format': '{point.hc-a2}',
                        'color': '#000000',
                        'style': {'textOutline': False}
                        },
                },
                {'data': data}],
        'credits': {'enabled': False}}
    return JsonResponse(chart)
