#!/usr/bin/env python
# encoding: utf-8
'''
forms.py -- Nymology database model forms
'''
from django import forms
from django.shortcuts import redirect
from django.template.defaultfilters import slugify

from .cached import QN
from .fields import ListTextWidget
from .models import Common, Fable, Phrase, Polynym, Polymap, Polyset, \
                    Quadranym, Quadraset, Queue, Story, Tale, Vectornym
from .sizers import polynym_size, qode_size, vectornym_size, polyset_size, quadraset_size
from .validators import MODES, POS, QODER


# FORM HELPER
def reform(form, fields=None, request=None):
    'merge fields to form.cleaned_data and redirect; add username if request'

    if fields is None:
        fields = []
    thing = form.save(commit=False)
    for field in fields:
        if field in form.cleaned_data:
            setattr(thing, field, form.cleaned_data[field])
    if request is not None:
        thing.user = request.user
    thing.slug = slugify(thing.name)
    thing.save()
    form.save_m2m()

    return redirect(f'/{thing.whois()}/{thing.pk}') # see edit

class CommonForm(forms.ModelForm):
    src = forms.CharField(label='Source', required=False)
    wiki = forms.URLField(label='URL', widget=forms.URLInput(attrs=dict(size=96)), required=False)
    class Meta:
        model = Common
        fields = ('name', 'src', 'wiki', 'area') # + user
    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

# COMMON FORMS
class FableForm(CommonForm):
    qode = forms.CharField(label='Template Qode',
                           widget=forms.Textarea(attrs=dict(rows=14, cols=64)),
                           validators=[QODER])
    class Meta:
        model = Fable
        fields = CommonForm.Meta.fields + ('qode', 'realm') # + subs, width, length
    def clean(self):
        data = super().clean()
        regx = QN.findall(data.get('qode', ''))
        if not regx:
            raise forms.ValidationError('')
        return qode_size(regx, data)

class PhraseForm(CommonForm):
    qode = forms.CharField(label='Template Qode',
                           widget=forms.Textarea(attrs=dict(rows=14, cols=64)),
                           validators=[QODER])
    class Meta:
        model = Phrase
        fields = CommonForm.Meta.fields + ('qode', 'realm') # + subs, width
    def clean(self):
        data = super().clean()
        regx = QN.findall(data.get('qode', ''))
        if not regx:
            raise forms.ValidationError('')
        data = qode_size(regx, data)
        if data.pop('length') > 1: # remove & check length
            raise forms.ValidationError('Too many topics!')
        return data

class PolynymForm(CommonForm):
    mode = forms.ChoiceField(choices=MODES)
    class Meta:
        model = Polynym
        fields = CommonForm.Meta.fields + ('mode', 'p1', 'p2', 'p3', 'p4', 'p5', 'p6',
                                           'p7', 'p8', 'p9', 'p10', 'p11', 'p12') # + depth
    def clean(self):
        return polynym_size(super().clean())

class PolymapForm(CommonForm):
    class Meta:
        model = Polymap
        fields = CommonForm.Meta.fields

class PolysetForm(CommonForm):
    polynyms = forms.ModelMultipleChoiceField(queryset=Polynym.data.all(),
                                              widget=forms.widgets.SelectMultiple(attrs={'size': 20}))
    class Meta:
        model = Polyset
        fields = CommonForm.Meta.fields + ('polynyms',)
    def clean(self):
        return polyset_size(super().clean())

class QuadranymForm(CommonForm):
    pos = epos = rpos = opos = spos = forms.ChoiceField(choices=POS, required=False)
    def __init__(self, *args, **kwargs):
        _data_list = kwargs.pop('data_list', None)
        super(QuadranymForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget = ListTextWidget(data_list=_data_list, name='name')
    class Meta:
        model = Quadranym
        fields = CommonForm.Meta.fields + ('pos', 'realm', 'e', 'r', 'o', 's',
                                           'epos', 'rpos', 'opos', 'spos')

class QuadrasetForm(CommonForm):
    quadranyms = forms.ModelMultipleChoiceField(queryset=Quadranym.data.all(),
                                                widget=forms.widgets.SelectMultiple(attrs={'size': 20}))
    class Meta:
        model = Quadraset
        fields = CommonForm.Meta.fields + ('quadranyms',)
    def clean(self):
        return quadraset_size(super().clean())

class StoryForm(CommonForm):
    class Meta:
        model = Story
        fields = CommonForm.Meta.fields + ('length', 'realm')

class TaleForm(CommonForm):
    class Meta:
        model = Tale
        fields = CommonForm.Meta.fields + ('length',)

class VectornymForm(CommonForm):
    class Meta:
        model = Vectornym
        fields = CommonForm.Meta.fields + ('v1', 'v2', 'v3', 'v4', 'v5', 'v6', 'v7', 'v8', 'v9')
    def clean(self):
        return vectornym_size(super().clean())

# GENERIC FORMS
class QueueForm(forms.ModelForm):
    class Meta:
        model = Queue
        fields = ('name',)
