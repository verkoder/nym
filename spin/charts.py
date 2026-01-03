#!/usr/bin/env python
# encoding: utf-8
'''
charts.py -- Nymology Highcharts plotting tools
'''
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
    for _abid, a, rels, b in sex:
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
        lo, hi, _av = data[ar]
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
