#!/usr/bin/env python
# encoding: utf-8
'''
serializers.py -- Nymology API data
'''
from rest_framework import serializers

from .cached import QN
from .models import Fable, Fortune, Phrase, Polynym, Polymap, Polyset, \
                    Quadranym, Quadraset, Queue, Quote, Story, Storyline, \
                    Tale, Taleline, Vectornym, Winner
from .sizers import polynym_size, qode_size, vectornym_size, polyset_size, quadraset_size
from .validators import QODER

COMMON_FIELDS = ['name', 'user', 'src', 'area', 'wiki', 'likes', 'voters']
DIRTY_FIELDS = ['src', 'area', 'wiki', 'likes', 'voters']


class CommonSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.CharField(source='user.username')
    class Meta:
        abstract = True
    def to_representation(self, obj):
        'omit empty fields from serial data'
        data = super().to_representation(obj)
        for field in self.Meta.dirty:
            if not getattr(obj, field):
                data.pop(field)
        data[f'{self.Meta.model.__name__.lower()}_id'] = obj.pk
        return data

# COMMONS - omit empty fields
class FableSerializer(CommonSerializer):
    class Meta:
        model = Fable
        dirty = DIRTY_FIELDS + ['realm']
        fields = COMMON_FIELDS + ['qode', 'subs', 'length', 'width', 'realm']
        validators = [QODER] # works!
    def validate(self, data):
        regx = QN.findall(data.get('qode', ''))
        if not regx:
            raise serializers.ValidationError('')
        return qode_size(regx, data)

class PhraseSerializer(CommonSerializer):
    class Meta:
        model = Phrase
        dirty = DIRTY_FIELDS + ['realm']
        fields = COMMON_FIELDS + ['qode', 'subs', 'width', 'realm']
        validators = [QODER]
    def validate(self, data):
        regx = QN.findall(data.get('qode', ''))
        if not regx:
            raise serializers.ValidationError('')
        data = qode_size(regx, data)
        if data.pop('length') > 1: # remove & check length
            raise serializers.ValidationError('Too many topics!')
        return data

class PolynymSerializer(CommonSerializer):
    class Meta:
        model = Polynym
        dirty = DIRTY_FIELDS + ['p3', 'p4', 'p5', 'p6', 'p7', 'p8', 'p9', 'p10', 'p11', 'p12']
        fields = COMMON_FIELDS + ['mode', 'depth', 'p1', 'p2', 'p3', 'p4', 'p5',
                                  'p6', 'p7', 'p8', 'p9', 'p10', 'p11', 'p12']
    def validate(self, data):
        return polynym_size(data)

class PolymapSerializer(CommonSerializer):
    pa = PolynymSerializer()
    pb = PolynymSerializer()
    class Meta:
        model = Polymap
        dirty = DIRTY_FIELDS + ['r3', 'r4', 'r5', 'r6', 'r7', 'r8', 'r9', 'r10', 'r11', 'r12']
        fields = COMMON_FIELDS + ['pa', 'pb', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6',
                                  'r7', 'r8', 'r9', 'r10', 'r11', 'r12']

class PolysetSerializer(CommonSerializer):
    polynyms = PolynymSerializer(many=True)
    class Meta:
        model = Polyset
        dirty = DIRTY_FIELDS
        fields = COMMON_FIELDS + ['polynyms', 'length', 'width', 'depth']
    def validate(self, data):
        return polyset_size(data)

class QuadranymSerializer(CommonSerializer):
    class Meta:
        model = Quadranym
        dirty = DIRTY_FIELDS + ['pos', 'epos', 'rpos', 'opos', 'spos', 'realm']
        fields = COMMON_FIELDS + ['e', 'r', 'o', 's', 'pos',
                                  'epos', 'rpos', 'opos', 'spos', 'realm']

class QuadrasetSerializer(CommonSerializer):
    quadranyms = QuadranymSerializer(many=True)
    class Meta:
        model = Quadraset
        dirty = DIRTY_FIELDS
        fields = COMMON_FIELDS + ['quadranyms', 'length']
    def validate(self, data):
        return quadraset_size(data)

class StorySerializer(CommonSerializer):
    class Meta:
        model = Story
        dirty = DIRTY_FIELDS + ['realm']
        fields = COMMON_FIELDS + ['length', 'realm']

class TaleSerializer(CommonSerializer):
    fable = FableSerializer()
    class Meta:
        model = Tale
        dirty = DIRTY_FIELDS
        fields = COMMON_FIELDS + ['length', 'fable']

class VectornymSerializer(CommonSerializer):
    v1 = PolynymSerializer()
    v2 = PolynymSerializer()
    v3 = PolynymSerializer()
    v4 = PolynymSerializer()
    v5 = PolynymSerializer()
    v6 = PolynymSerializer()
    v7 = PolynymSerializer()
    v8 = PolynymSerializer()
    v9 = PolynymSerializer()
    class Meta:
        model = Vectornym
        dirty = DIRTY_FIELDS + ['v3', 'v4', 'v5', 'v6', 'v7', 'v8', 'v9', 'realm']
        fields = COMMON_FIELDS + ['length', 'width', 'depth', 'v1', 'v2',
                                  'v3', 'v4', 'v5', 'v6', 'v7', 'v8', 'v9', 'realm']
    def validate(self, data):
        return vectornym_size(data)

# UNCOMMONS - serialize all data
class UncommonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        abstract = True
    def to_representation(self, obj):
        data = super().to_representation(obj)
        data[f'{self.Meta.model.__name__.lower()}_id'] = obj.pk
        return data

class QuadranymPicker(UncommonSerializer):
    class Meta:
        model = Quadranym
        fields = ['name']

class QueueSerializer(UncommonSerializer):
    class Meta:
        model = Queue
        fields = ['name']

class QuoteSerializer(UncommonSerializer):
    quadranym = QuadranymSerializer()
    class Meta:
        model = Quote
        fields = ['body', 'qode', 'quadranym', 'subs', 'width', 'src']

class FortuneSerializer(UncommonSerializer):
    q1 = QuadranymSerializer(many=True)
    q2 = QuadranymSerializer(many=True)
    class Meta:
        model = Fortune
        fields = ['body', 'qode', 'q1', 'q2', 'subs', 'depth']

class StorylineSerializer(UncommonSerializer):
    phrase = PhraseSerializer()
    quadranym = QuadranymSerializer()
    story = StorySerializer()
    class Meta:
        model = Storyline
        fields = ['rank', 'story', 'phrase', 'quadranym']

class TalelineSerializer(UncommonSerializer):
    tale = TaleSerializer()
    quadranym = QuadranymSerializer()
    class Meta:
        model = Taleline
        fields = ['rank', 'tale', 'quadranym']

class WinnerSerializer(UncommonSerializer):
    user = serializers.CharField(source='user.username')
    class Meta:
        model = Winner
        fields = ['by', 'user', 'app', 'score', 'round']
