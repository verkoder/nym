#!/usr/bin/env python
'''
datafix.py -- Nymology data tools
'''
from django.template.defaultfilters import slugify
from spin.models import COMMON

def add_slugs():
    for labl,common in COMMON.items():
        data = common.objects.all()
        print(f'Slugifying {len(data)} items')
        for obj in data:
            obj.slug = slugify(obj.name)
            obj.save()
