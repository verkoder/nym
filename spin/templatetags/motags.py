from django import template
from django.utils.safestring import mark_safe
register = template.Library()

@register.simple_tag
def voted_on(user, thing):
    'all Common detail views'

    if not thing.votes.exists(user):
        return 'Vote?'
    return 'Voted!'

@register.filter
def istuple(value):
    'trace_tale'

    return isinstance(value, tuple)

@register.filter
def index(indexable, i):
    'trace_tale'

    return indexable[i]

@register.filter()
def nbsp(value):
    'home page'

    return mark_safe("&nbsp;".join(value.split(' ')))
