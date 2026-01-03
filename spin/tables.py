#!/usr/bin/env python
# encoding: utf-8
'''
tables.py -- Nymology sort list tables
'''
import django_tables2 as tables
from django.utils.html import format_html

from .methods import wikify
from .models import Quadranym, Polynym

class CommonTable(tables.Table):
    id = tables.Column(verbose_name='')
    name = tables.Column(verbose_name='Name / URL')
    class Meta:
        abstract = True

    def render_id(self, value):
        return format_html(
            f'<a href="/{self.Meta.model.__name__.lower()}/update/{value}"><i class="fas fa-edit"></i></a><br>'
            f'<a href="/{self.Meta.model.__name__.lower()}/delete/{value}"><i class="fas fa-trash-alt"></i></a> '
        )

    def render_name(self, value, record):
        return format_html(
            f'<a href="/{self.Meta.model.__name__.lower()}/{record.pk}"><b>{value}</b></a><br>'
            f'<small><a href="{record.wiki}" target="_blank"><b>{wikify(record.wiki)}</b></a></small>'
        )

    def render_user(self, value):
        return format_html(f'<small class="text-muted">{value}</small>')

class QuadranymTable(CommonTable):
    class Meta:
        model = Quadranym
        attrs = {'class': 'commons table table-dark table-responsive table-striped table-hover text-left w-100 d-block d-md-table mb-0'}
        fields = ('id', 'name', 'area', 'src', 'realm', 'e', 'r', 'o', 's', 'pos', 'user')
    def render_pos(self, value):
        return format_html(f'<small class="text-muted">{value}</small>')
    def render_e(self, value, record):
        return value if not record.epos else format_html(f'{value}<br><small class="text-muted">{record.epos}</small>')
    def render_r(self, value, record):
        return value if not record.rpos else format_html(f'{value}<br><small class="text-muted">{record.rpos}</small>')
    def render_o(self, value, record):
        return value if not record.opos else format_html(f'{value}<br><small class="text-muted">{record.opos}</small>')
    def render_s(self, value, record):
        return value if not record.spos else format_html(f'{value}<br><small class="text-muted">{record.spos}</small>')

class PolynymTable(CommonTable):
    p1 = tables.Column(verbose_name='Dimensions')
    class Meta:
        model = Polynym
        attrs = {'class': 'commons table table-dark table-responsive table-striped table-hover text-left w-100 d-block d-md-table mb-0'}
        fields = ('id', 'name', 'area', 'src', 'mode', 'depth', 'p1', 'user')

    def render_p1(self, value, record):
        return format_html(' <span class="text-muted">|</span> '.join(record.nyms()))
