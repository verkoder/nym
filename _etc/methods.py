
def choosify(obj, request=None, attr='pk', pk=None):
    'get item from request[attr] or choice'
    things = orderfy(obj)
    if pk is not None:
        try:
            return things, things.get(pk=pk)
        except obj.DoesNotExist:
            return things, choice(things)
    try:
        return things, things.get(pk=request.POST[attr])
    except (KeyError, AttributeError, obj.DoesNotExist):
        return things, choice(things)

def orderfy(obj=None, n=None):
    'ordered list of Common objects'
    if obj is Polynym: # omit FMK, moodsets
        return Polynym.objects.filter(depth=n) \
                              .exclude(name__in=['~fmk', 'moodset']) \
                              .order_by(Lower('name')) if n is not None else \
               Polynym.objects.exclude(name__in=['~fmk', 'moodset']) \
                              .order_by(Lower('name'))
    if obj is Quadranym: # omit line break, topic
        return Quadranym.objects.exclude(name__in=['-', '--', '~Topic~']) \
                                .order_by(Lower('name'))
    if obj is Phrase: # omit line break
        return Phrase.objects.exclude(name='-').order_by(Lower('name'))
    if obj is Quote: # sort by source
        return Quote.objects.all().order_by(Lower('src'))
    if obj is Fortune: # only 2+ codimensions
        return Fortune.objects.exclude(q2=None).order_by(Lower('body'))
    if obj is Queue: # undone to-do qQ
        return sorted(list({x.name for x in Queue.objects.all()} \
                         - {x.name for x in thingify(Quadranym)}))
    return obj.objects.all().order_by(Lower('name')) if obj is not None else \
           sorted(list({x.name for x in thingify(Quadranym)} \
                     & {x.name for x in Queue.objects.all()})) # done to-do qQ

def samplify(obj, request=None, attr='pk', size=None, rev=None):
    'getlist from request[attr] or sample'
    msg = None
    things = list(orderfy(obj))
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

def dimension_dict(commons):
    'nym dimensional dictionary'
    words = {}
    for common in commons:
        for nym in common.nyms(True):
            if not nym in words:
                words[nym] = {common}
            else:
                words[nym].add(common)
    return words

def do_dict(form_list): # see CommonWizard
    'dict from forms'
    data = [form.cleaned_data for form in form_list]
    return {k: v for d in data for k, v in d.items()}

def enqodes(q_list, text):
    'enqode via Quadranym list: FIFO'
    for i, q in enumerate(q_list, 1):
        text = q.enqode(text, i)
    return text

def poly_search(word, polys): #now part of poly_table
    'dimensional word lookup/count'
    got = {}
    dims = {x:0 for x in range(1, 13)} # dimension log
    for p in polys:
        nyms = dict([(getattr(p, f'p{x}'), p.depth) for x in range(1, 13)] + [(p.name, p.depth)])
        if word in nyms:
            dim = nyms[word]
            dims[dim] += 1
            if not dim in got:
                got[dim] = [p]
            else:
                got[dim].append(p)
    return got, dims
