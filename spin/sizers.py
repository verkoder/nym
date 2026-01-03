#!/usr/bin/env python
# encoding: utf-8
'''
sizers.py -- Nymology form/serial data size counters
'''


def polynym_size(data):
    data['depth'] = len([x for x in [data[f'p{p}'] for p in range(1, 13)] if x])
    return data

def polyset_size(data):
    data['length'] = len(data['polynyms']) # many-to-many
    data['width'] = len([x for y in [
        p.nyms() for p in data['polynyms']] for x in y])
    data['depth'] = max([p.depth for p in data['polynyms']])
    return data

def quadraset_size(data):
    data['length'] = len(data['quadranyms'])
    return data

def qode_size(regx, data):
    'Phrase / Fable'
    data['subs'] = ''.join([x[1] for x in regx]).upper()
    data['width'] = len(regx)
    data['length'] = max([int(x[0]) for x in regx])
    return data

def vectornym_size(data):
    depth = length = width = 0
    for i in range(1, 10):
        if data[f'v{i}'] != 'None':
            poly = data[f'v{i}']
            if poly:
                length += 1
                width += poly.depth
                if poly.depth > depth:
                    depth = poly.depth
    data['depth'] = depth
    data['length'] = length
    data['width'] = width
    return data
