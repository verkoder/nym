#!/usr/bin/env python
# encoding: utf-8
'''
motags.py -- Nymology template tags
'''
from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from spin.models import wikify
from spin.views import COMMON

register = template.Library()

@register.simple_tag
def voted_on(user, thing):
    'used in detail views for all Common classes'

    if not thing.votes.exists(user):
        return 'Vote?'
    return 'Voted!'

@register.filter
def nymsake(nyms, common):
    'common objects by nyms'

    things = COMMON[common].objects.filter(name__in=nyms)
    if things:
        if common != 'quadranym':
            return format_html(f'Related {common.title()}s: '+' &nbsp; • &nbsp; '.join([
                f'<a href="/{common}/{x.pk}">{x.name} ({x.src})</a>' if x.src else \
                f'<a href="/{common}/{x.pk}">{x.name}</a>' for x in things]))
        return format_html(''.join([
            f'<br>Related Quadranym: <a href="/{common}/{x.pk}">{x.name} ({x.src})</a><br>{quoted(x)}' if x.src else \
            f'<br>Related Quadranym: <a href="/{common}/{x.pk}">{x.name}</a><br>{quoted(x)}' for x in things
        ]))

@register.filter
def quoted(quadranym):
    'quotes by quadranym'

    things = COMMON['quote'].objects.filter(quadranym=quadranym)
    if things:
        return format_html(f'Related Quotes: '+' &nbsp; • &nbsp; '.join([
            f'<a href="/turnquote/{x.pk}">{x.subs} ({x.src})</a>' if x.src and x.src else \
            f'<a href="/turnquote/{x.pk}">{x.subs}</a>' if x.name else \
            f'<a href="/turnquote/{x.pk}">{x.quadranym.name}</a>' for x in things]))
    return ''

@register.filter
def wikurl(value):
    'add wikipedia logo'

    return format_html(wikify(value))

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
