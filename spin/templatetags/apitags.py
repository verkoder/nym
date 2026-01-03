#!/usr/bin/env python
# encoding: utf-8
'''
apitags.py -- Nymology API tags
'''
from django import template

from spin.urls import router

ENDPOINTS = {
    'data': [
        x.pattern.regex.pattern[1:].split('/')[0] for x in router.urls \
            if x.name.endswith('ail') and x.pattern.regex.pattern.endswith('/$')
    ]
}
register = template.Library()

@register.filter
def endpoints(data):
    'API endpoints: Data Lists'
    return ENDPOINTS[data]
