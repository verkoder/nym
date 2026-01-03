### WIP
## HTML script
# <!--{% elif typ == 'tilemap' %}
# <script src="https://code.highcharts.com/maps/highmaps.js"></script>
# <script src="https://code.highcharts.com/modules/tilemap.js"></script>-->
## plot.html TILEMAP SHITSHOW
## <!--<b>Polynymic Table:</b> <label style="white-space: nowrap;"><input type="radio" name="typ" value="tilemap"{% if typ == "tilemap" %} checked{% endif %}>Tile Map</label><br>-->

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
