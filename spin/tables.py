#!/usr/bin/env python
# encoding: utf-8
'''
tables.py -- Nymology sort list tables
'''
import django_tables2 as tables
from django.utils.html import format_html

from .models import Common, Quadranym, Polynym, wikify

class CommonTable(tables.Table):
    class Meta:
        model = Common
        name = tables.Column(order_by=('name', 'src'))
        exclude = ('num_vote_up', 'num_vote_down', 'vote_score')

    def render_name(self, value, record):
        return format_html(f'<a href="/{self.Meta.model.__name__.lower()}/{record.pk}"><b>{value}</b></a>')

    def render_id(self, value):
        return format_html(
            f'<a href="/{self.Meta.model.__name__.lower()}/update/{value}">&check;</a><br>'
            f'<a href="/{self.Meta.model.__name__.lower()}/delete/{value}">&timesb;</a> '
        )

    def render_wiki(self, value):
        return format_html(f'<a href="{value}" target="_blank"><b>{wikify(value)}</b></a>')

class QuadranymTable(CommonTable):
    class Meta:
        model = Quadranym
        attrs = {'class': 'commons'}
        fields = ('id', 'name', 'area', 'src', 'user', 'realm', 'e', 'r', 'o', 's',
                  'pos', 'epos', 'rpos', 'opos', 'spos', 'wiki')

class PolynymTable(CommonTable):
    class Meta:
        model = Polynym
        attrs = {'class': 'commons'}
        fields = ('id', 'name', 'area', 'src', 'user', 'mode', 'depth', 'p1', 'p2', 'p3',
                  'p4', 'p5', 'p6', 'p7', 'p8', 'p9', 'p10', 'p11', 'p12', 'wiki')
