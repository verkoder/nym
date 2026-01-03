import re
import json
import scrapy

DNE = 'Wikipedia does not have an article with this exact name.'
COLON = re.compile(r'(?:\w:\s+|—)')
PARENDOT = re.compile(r'(?:\s+\(.+?\)\.?)|(?:\.)')
INPAREN = re.compile(r'\((.+?)\)')
PUNC = re.compile(r'(\.|,|;|:|\(|\))')
CURLY = re.compile(r'\{.+\}')

AND = re.compile(r'(?:,?\s+(?:and|or)\s+|\s+&\s+)(?!which)') # split devices
ANDCOMMA = re.compile(r'(?:,?\s+(?:and|or)\s+|,\s+|\s+&\s+)(?!which)')
COMMA = re.compile(r'(?:,\s+)(?!which)')
DASH = re.compile(r'(?:\s+-\s+)')
SEMI = re.compile(r'(?:\b;\s+(?:and\s+)?)')

CITS = re.compile(r'\[(\d+|citation needed)\]')
TAGS = re.compile(r'<[^>]*?>')
FTHS = re.compile(r'(?is)(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|eleventh|twelfth)')

SENT = re.compile(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s+')

_F = r'(?is)(?<!-)\b'
_B = (r'\b(?!(-|\s+)(article|centur|children|days|daughter|decade|dozen|book|film|month|or more|other|'
      r'sons|studies|television|tenth|the present|times|trigram|volume|year|1|2|3|4|5|6|7|8|9|0))')
POLYS = {
    2: re.compile(_F + r'(both|double|dual|pair|two(-part)?)' + _B),
    3: re.compile(_F + r'(three(-part)?|triple)' + _B),
    4: re.compile(_F + r'(four(-part)?)' + _B),
    6: re.compile(_F + r'(six(-part)?)' + _B),
    5: re.compile(_F + r'(five(-part)?)' + _B),
    7: re.compile(_F + r'(seven(-part)?)' + _B),
    8: re.compile(_F + r'(eight(-part)?)' + _B),
    9: re.compile(_F + r'(nine(-part)?)' + _B),
    10: re.compile(_F + r'(ten(-part)?)' + _B),
    11: re.compile(_F + r'(eleven(-part)?)' + _B),
    12: re.compile(_F + r'(twelve(-part)?)' + _B)
}
NAME_URLS = [(x['name'], x['wiki']) for x in json.load(open('./data/polywikis.json')) if x['wiki']]

URLS = set([x[1] for x in NAME_URLS])
NODES = {x['word'] for x in json.load(open('./data/polynodes.json'))}
NODE_URLS = [(y, z) for y,z in [(x, f'https://en.wikipedia.org/wiki/{PARENDOT.sub("", x.replace(" ", "_"))}'
                                ) for x in NODES if not x.endswith('.')] if not z in URLS]


def nodesplit(text, para, depth):
    'try parsing nodes at depth'
    tts = INPAREN.findall(text)
    text = PARENDOT.sub('', text)
    col = COLON.search(text)
    tts.append(text[col.span()[1]:] if (col and len(text) - col.span()[1] > 12) else text)
    tts = [x for x in tts if x]
    for text in tts:
        for regx in (SEMI, AND, ANDCOMMA, COMMA, DASH):
            nodes = regx.split(text)
            if len([x for x in nodes if FTHS.search(x)]) == depth:
                return [PUNC.sub('', x) for x in [x for x in nodes if FTHS.search(x)]]
            if len(nodes) == depth:
                return [PUNC.sub('', x) for x in nodes]
    nodes = [x for x in SENT.split(para) if FTHS.search(x)]
    if len(nodes) == depth:
        return [PUNC.sub('', x) for x in nodes]
    return []

def chunkpara(paras):
    'combine colon-ended paragraphs; remove citations/tags'
    nu = []
    paras = [CITS.sub('', TAGS.sub('', x.get())) for x in paras]
    while paras:
        para = paras.pop(0).strip()
        nu.append(f'{para}\n\t{paras.pop(0)}' if (para.endswith(':') and paras) else para)
    return nu

def chunksent(para):
    'combine short sentences'
    nu = []
    sents = [x for x in SENT.split(para) if x]
    while sents:
        sent = sents.pop(0).strip()
        nu.append(f'{sent} {sents.pop(0)}' if (len(sent) < 50 and sents) else sent)
    return nu

class WikiSpider(scrapy.Spider):
    'STEP 2: crawl Polynym URLs for guesses'
    name = 'wikipedia'
    seen = set()
    start_urls = []

    async def start(self):
        for name,url in NAME_URLS:
            yield scrapy.Request(url=url, callback=self.parse, meta={'name': name})
        for node,url in NODE_URLS:
            yield scrapy.Request(url=url, callback=self.parse, meta={'name': node})

    def parse(self, response):
        if DNE in response.text:
            yield
        for para in chunkpara(response.css('p')):
            para = CURLY.sub('', para)
            for sent in chunksent(para):
                for depth,regx in POLYS.items():
                    for mat in regx.finditer(sent):
                        data = {
                            'name': response.meta['name'],
                            'depth': depth,
                            'paragraph': para,
                            'sentence': sent,
                            'wiki': response.url,
                            'word': mat.group(0).lower()
                        }
                        for i,node in enumerate(nodesplit(sent[mat.span()[1]:], para, depth)):
                            data[f'p{i+1}'] = node
                        if 'p1' in data:
                            test = hash(frozenset([(k,v) for k,v in data.items() if not k in ('paragraph', 'sentence', 'word')]))
                        else:
                            test = hash(frozenset(data.items()))
                        if test in self.seen:
                            continue
                        self.seen.add(test)
                        yield data

