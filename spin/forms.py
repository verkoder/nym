from django import forms
from django.shortcuts import redirect
from django.core.validators import RegexValidator

from .models import Common, Polynym, Quadranym, Polyset, Quadraset, \
                    Fable, Phrase, Queue, QN, orderfy
from .fields import ListTextWidget

QODER = RegexValidator(regex=QN, message='Empty qode script!')

def subs_width(data):
    subs = ''.join([x.group(2) for x in QN.finditer(data.get('qode', ''))]).upper()
    data['subs'] = subs
    data['width'] = len(subs)
    return data

def polynym_depth(data):
    data['depth'] = len([x for x in [data[f'p{p}'] for p in range(1, 13)] if x])
    return data

def quadranym_length(data):
    data['length'] = len(data['quadranyms'])
    return data

# FORM HELPER
def reform(form, fields=[], request=None):
    'merge fields to form.cleaned_data and redirect; add username if request'

    thing = form.save(commit=False)
    for field in fields:
        if field in form.cleaned_data:
            setattr(thing, field, form.cleaned_data[field])
    if request is not None:
        thing.user = request.user
    thing.save()
    form.save_m2m()

    return redirect(f'/{thing.whois()}/{thing.pk}') # see edit

##################
### ROOT FORMS ###
class NoForm(forms.ModelForm):
    class Meta:
        model = Common
        fields = [] # + user
    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

class CommonForm(NoForm):
    src = forms.CharField(label='Source', required=False)
    wiki = forms.URLField(label='URL', widget=forms.URLInput(attrs=dict(size=96)), required=False)
    class Meta:
        model = Common
        fields = ('name', 'src', 'wiki', 'area') # + user

####################
### COMMON FORMS ###
class PhraseForm(CommonForm):
    qode = forms.CharField(label='Template Qode',
                           widget=forms.Textarea(attrs=dict(rows=14, cols=64)),
                           validators=[QODER])
    class Meta:
        model = Phrase
        fields = CommonForm.Meta.fields + ('qode', 'realm') # + subs, width
    def clean(self):
        return subs_width(super(PhraseForm, self).clean())

class FableForm(PhraseForm):
    class Meta:
        model = Fable
        fields = PhraseForm.Meta.fields # + subs, width
    def clean(self):
        return subs_width(super(FableForm, self).clean())

class PolynymForm(CommonForm):
    MODES = (('', '<< Mode >>'), ('type', 'Type / Kind / Method'),
             ('part', 'Part / Piece / Area'), ('step', 'Step / Stage / Level'))
    mode = forms.ChoiceField(choices=MODES)
    class Meta:
        model = Polynym
        fields = CommonForm.Meta.fields + ('mode', 'p1', 'p2', 'p3', 'p4', 'p5', 'p6',
                                           'p7', 'p8', 'p9', 'p10', 'p11', 'p12') # + depth
    def clean(self):
        return polynym_depth(super(PolynymForm, self).clean())

class QuadranymForm(CommonForm):
    POS = (('', '<< Part-of-Speech >>'), ('NN', 'Noun (NN)'),
           ('VB', 'Verb (VB)'), ('ADJ', 'Adjective (ADJ)'))
    pos = epos = rpos = opos = spos = forms.ChoiceField(choices=POS, required=False)
    def __init__(self, *args, **kwargs):
        _data_list = kwargs.pop('data_list', None)
        super(QuadranymForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget = ListTextWidget(data_list=_data_list, name='name')
    class Meta:
        model = Quadranym
        fields = CommonForm.Meta.fields + ('pos', 'realm', 'e', 'r', 'o', 's',
                                           'epos', 'rpos', 'opos', 'spos')

class PolysetForm(CommonForm):
    polynyms = forms.ModelMultipleChoiceField(queryset=orderfy(Polynym),
                                              widget=forms.widgets.SelectMultiple(attrs={'size': 20}))
    class Meta:
        model = Polyset
        fields = CommonForm.Meta.fields + ('polynyms',)
    def clean(self):
        cleaned_data = super(PolysetForm, self).clean()
        cleaned_data['length'] = len(cleaned_data['polynyms']) # many-to-many
        cleaned_data['width'] = len([x for y in [
            p.nyms() for p in cleaned_data['polynyms']] for x in y])
        cleaned_data['depth'] = max([p.depth for p in cleaned_data['polynyms']])
        return cleaned_data

class QuadrasetForm(CommonForm):
    quadranyms = forms.ModelMultipleChoiceField(queryset=orderfy(Quadranym),
                                                widget=forms.widgets.SelectMultiple(attrs={'size': 20}))
    class Meta:
        model = Quadraset
        fields = CommonForm.Meta.fields + ('quadranyms',)
    def clean(self):
        return quadranym_length(super(QuadrasetForm, self).clean())

#######################
### SPECIAL CLASSES ###
class QueueForm(forms.ModelForm):
    class Meta:
        model = Queue
        fields = ('name',)
