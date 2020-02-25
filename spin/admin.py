from django.db import models
from django.contrib import admin
from django.forms import TextInput

# NYMOLOGY CLASSES
from .models import Polynym, Polymap, Polyset, Quadranym, Quadraset, \
                    Fable, Phrase, Story, Storyline, Tale, Taleline, \
                    Fortune, Queue, Quote, Vectornym, Winner

class BaseAdmin(admin.ModelAdmin):
    formfield_overrides = {models.CharField: {'widget': TextInput(attrs={'size': '142'})}}
    ordering = ('name',)
class FableAdmin(BaseAdmin):
    pass
class FortuneAdmin(BaseAdmin):
    ordering = ('body',)
class PhraseAdmin(BaseAdmin):
    pass
class PolymapAdmin(BaseAdmin):
    pass
class PolynymAdmin(BaseAdmin):
    pass
class PolysetAdmin(BaseAdmin):
    pass
class QuadranymAdmin(BaseAdmin):
    pass
class QueueAdmin(BaseAdmin):
    pass
class QuadrasetAdmin(BaseAdmin):
    pass
class QuoteAdmin(BaseAdmin):
    ordering = ('src',)
class StoryAdmin(BaseAdmin):
    pass
class StorylineAdmin(BaseAdmin):
    ordering = ('story', 'rank')
class VectornymAdmin(BaseAdmin):
    pass
class TaleAdmin(BaseAdmin):
    pass
class TalelineAdmin(BaseAdmin):
    ordering = ('tale', 'rank')
class WinnerAdmin(BaseAdmin):
    ordering = ('score',)

admin.site.register(Fable, FableAdmin)
admin.site.register(Fortune, FortuneAdmin)
admin.site.register(Phrase, PhraseAdmin)
admin.site.register(Polymap, PolymapAdmin)
admin.site.register(Polynym, PolynymAdmin)
admin.site.register(Polyset, PolysetAdmin)
admin.site.register(Quadranym, QuadranymAdmin)
admin.site.register(Queue, QueueAdmin)
admin.site.register(Quadraset, QuadrasetAdmin)
admin.site.register(Quote, QuoteAdmin)
admin.site.register(Story, StoryAdmin)
admin.site.register(Storyline, StorylineAdmin)
admin.site.register(Vectornym, VectornymAdmin)
admin.site.register(Tale, TaleAdmin)
admin.site.register(Taleline, TalelineAdmin)
admin.site.register(Winner, WinnerAdmin)
