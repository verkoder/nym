#!/usr/bin/env python
# encoding: utf-8
'''
dataset.py -- Nymology data
Import Nymbase data from:
  - nymbase.pkl -- legacy qControl app data
'''
import re
import pickle
import subprocess

from spin.models import Polynym, Quadranym, Phrase, QN

Q = re.compile(r'q(T|E|R|O|S)') # legacy qT format
QT = re.compile(r'(?i)q(\d)*?(T|E|R|O|S)') # legacy q1T format

def fix_qode(qode, number=1):
    'update legacy qT and q1T qode to new q1n format'

    matches = list(QT.finditer(qode))
    matches.reverse() # start at end
    for m in matches:
        n = m.group(1) # txt number overrides input
        q = m.group(2).lower() # dimension(t,e,r,o,s)
        q = q if q != 't' else 'n' # update t/T(opic) to n(ame)
        qode = f'{qode[:m.start()]}q{number if not n else n}{q}{qode[m.end():]}'
    return qode

def nymbase():
    '''backup nymbase pickle, add POS/Z, toss date, fix fields:
            t/title=>name
            author=>by
            source=>src
            used=>mode
            poly=>p'''

    subprocess.run("rm -f db.sqlite3", shell=True, check=True)
    subprocess.run("rm -f data/nymbase.pkl", shell=True, check=True)
    subprocess.run("cp data/nymbase_bk.pkl data/nymbase.pkl", shell=True, check=True)
    base = pickle.load(open('data/nymbase.pkl', 'rb'))
    nu_base = {}

    for nym in base.keys():
        nu = []
        pos = None
        if nym in ('noung', 'nouns'):
            pos = 'NN'
        elif nym in ('verbg', 'verbs'):
            pos = 'VB'
        z = None
        if nym in ('nouns', 'verbs'): # Z-TOPIC
            z = 0
        elif nym in ('ztopics', 'e_ztopics', 'verbg', 'noung'):
            z = 1

        for this in base[nym]:
            if z is not None:                   # z
                this['z'] = z
            if pos is not None:                 # POS
                this['pos'] = pos
            if 'title' in this:                 # name
                this['name'] = this.pop('title')
            elif 't' in this:
                this['name'] = this.pop('t')
            if 'source' in this:                # src
                this['src'] = this.pop('source')
            if 'author' in this:                # by
                this['by'] = this.pop('author')
            if 'poly' in this:                  # p > depth
                this['depth'] = this.pop('poly')
            if 'used' in this:                  # mode
                this['mode'] = this.pop('used')
            if 'date' in this:                  # date
                del this['date'] # <<!TOSS DATA!<<
            if nym in ('e_nouns', 'e_ztopics'): # subs/depth
                this['qode'] = fix_qode(this.pop('body'))
                subs = [x.group(2) for x in QN.finditer(this['qode'])]
                this['subs'] = ''.join(subs).upper()
                this['width'] = len(subs) # here, depth == len(subs)
            elif nym == 'nyms': # p1,p2..
                segs = this.pop('body').split(',')
                for i, seg in enumerate(segs):
                    i += 1
                    this['p%i' % i] = seg
            nu.append(this)
        nu_base[nym] = nu
    pickle.dump(nu_base, open('data/nymbase.pkl', 'wb'))

def dj_nymbase():
    'add all Nymbase => django: Polynym, Quadranym, Phrase'

    base = pickle.load(open('data/nymbase.pkl', 'rb'))
    for nym in ('nouns', 'noung', 'verbs', 'verbg', 'ztopics', 'nyms', 'e_nouns', 'e_ztopics'):
        data = base[nym]
        print(f'\ndatabase[{nym}]')

        if nym in ('nouns', 'noung', 'verbs', 'verbg', 'ztopics'):
            for this in data:
                print(f"nym[{this.get('name', 'UNKNOWN')}]")
                quad = Quadranym(**this)
                quad.save()
        elif nym in ('e_nouns', 'e_ztopics'):
            for this in data:
                print(f"nym[{this['name']}]")
                phra = Phrase(**this)
                phra.save()
        else:
            for this in data:
                print(f"nym[{this['name']}]")
                poly = Polynym(**this)
                poly.save()
