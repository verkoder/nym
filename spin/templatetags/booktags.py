#!/usr/bin/env python
# encoding: utf-8
'''
motags.py -- Nymology template tags
'''
from django import template
from spin.cached import QTAG


register = template.Library()

@register.filter
def unbold(text):
    'used in bits/book'
    return text.replace('<b>', '').replace('</b>', '')

@register.filter
def embolden(text):
    'used in bits/book'
    return QTAG.sub(r'<b>\1</b>', text)

@register.filter
def blanken(text):
    'used in bits/qode'
    return QTAG.sub('_____', text)

@register.filter
def gradlibs(text):
    'used in bits/book'
    return QTAG.sub(r'<u><b>&nbsp;&nbsp;\3&nbsp;</b></u><sup>\2</sup>', text)
