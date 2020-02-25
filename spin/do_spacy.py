'''
do_spacy.py -- spaCy NLP tools with pyinflect
'''
from functools import wraps
from string import punctuation
from collections import Counter

import pyinflect
from nym.settings import DOC # SERVER | DOC = spacy.tokens.doc.Doc
from nym.settings import ENGLISH #    | ENGLISH = spacy.load('en_core_web_lg')

# DECORATOR
def sp(meth):
    'allow methods to input free text or spaCy Doc'

    @wraps(meth)
    def sp_meth(*args, **kwargs): # use spaCy only if needed..
        args = [ENGLISH(x) if not isinstance(x, DOC) else x for x in args]
        kwargs = {k:ENGLISH(x) if not isinstance(x, DOC) else x for k, x in kwargs.items()}
        return meth(*args, **kwargs)
    return sp_meth

#####################
### SPACY METHODS ###
def qsim(q):
    'get similarity for all Q dimension pairs'

    return sim(q.nyms(named=True))

def sim(docs):
    'get similarity for multiple items'

    docs = [eat(x) for x in docs]
    return [(x, [(y, x.similarity(y)) for y in docs]) for x in docs]

@sp
def eat(doc):
    'digest text to spaCy doc'

    return doc

@sp
def toke(doc):
    'tokenize input'

    return [x.text for x in doc]

def retoke(tokes):
    'retokenize tokens to spaCy Doc'

    spaces = [True for x in tokes]
    spaces[-1] = False # remove trailing space

    for i, x in enumerate(tokes):
        if x in punctuation: # if punc..
            spaces[i - 1] = False # ..remove preceding space

    return DOC(ENGLISH.vocab, words=tokes, spaces=spaces)

@sp
def pos(doc):
    'tag part-of-speech'

    return [(x, x.pos_) for x in doc]

@sp
def ner(doc):
    'get named entities'

    return [(x, x.label_) for x in doc.ents]

@sp
def lemma(doc):
    'lemmatize text'

    return [(x, x.lemma_) for x in doc]

@sp
def unstop(doc):
    'remove stopwords'

    return [x.text for x in doc if not x.is_stop and not x.is_punct]

@sp
def chunks(doc):
    'get noun chunks'

    return [x.text for x in doc.noun_chunks]

@sp
def tree(doc):
    'get dependency tree'

    return [(x.text, x.dep_, x.head.text, x.head.pos_, list(x.children)) for x in doc]

@sp
def wordcount(doc):
    'calculate word frequency'

    freq = Counter(unstop(doc))
    return freq.most_common(4)

#########################
### PYINFLECT METHODS ###
def inflect(doc, word, inflection):
    'modify a doc.word by inflection'

    try:
        dic = {y.__str__():x for x, y in enumerate(doc)}
        return doc[dic[word]]._.inflect(inflection)
    except KeyError:
        return word
