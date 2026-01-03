#!/usr/bin/env python
# encoding: utf-8
'''
urls.py -- Nymology spin app url patterns
'''
from django.urls import include, path
from rest_framework import routers
from . import views
app_name = 'spin'

router = routers.DefaultRouter()
router.get_api_root_view().cls.__name__ = 'Nymology'
router.get_api_root_view().cls.__doc__ = 'API endpoints'
router.register(r'fable', views.FableViewSet)
router.register(r'fortune', views.FortuneViewSet)
router.register(r'phrase', views.PhraseViewSet)
router.register(r'polynym', views.PolynymViewSet)
router.register(r'polymap', views.PolymapViewSet)
router.register(r'polyset', views.PolysetViewSet)
router.register(r'quadranym', views.QuadranymViewSet)
router.register(r'quadranym-id', views.QuadranymPicks, 'API-Quadranym')
router.register(r'quadraset', views.QuadrasetViewSet)
router.register(r'queue', views.QueueViewSet)
router.register(r'quote', views.QuoteViewSet)
router.register(r'story', views.StoryViewSet)
router.register(r'tale', views.TaleViewSet)
router.register(r'storyline', views.StorylineViewSet)
router.register(r'taleline', views.TalelineViewSet)
router.register(r'vectornym', views.VectornymViewSet)
router.register(r'winner', views.WinnerViewSet)

urlpatterns = [
    path('',                            views.index_vu,                name='home'),      # HOME
    path('taper/',                      views.taper_vu),
    path('api/',                        include(router.urls)),                            # API
    path('info/api/',                   views.info_api,                name='api_info'),  # API INFO
    path('info/',                       views.info_site,               name='site_info'), # SITE INFO
    path('play/',                       views.play_vu,                 name='play'),      # PLAYGROUND
    path('accounts/',                   include('django.contrib.auth.urls')),             # AUTH
    path('signup/',                     views.SignUp.as_view(),        name='signup'),    # SIGNUP
    path('user/<str:username>',         views.user_vu,                 name='user_detail'), # USER
    path('<str:com>/<int:pk>/vote/<str:io>/', views.CommonVote.as_view()),                  # VOTE
#   path('api/yo/<str:sup>/',           views.yo_world),                         # API methods WIP
#   path('wiz/',                        views.FormWizardView.as_view(), name='wiz'),     # wiz WIP

    path('polynym/',                 views.PolynymDetail.as_view(), name='polynym_detail'), # POLYNYM
    path('polynym/<int:pk>/',        views.PolynymDetail.as_view(), name='polynym_detail'),
    path('polynym/update/<int:pk>',  views.PolynymUpdate.as_view(), name='polynym_update'),
    path('polynym/delete/<int:pk>',  views.PolynymDelete.as_view(), name='polynym_delete'),
    path('polynym/add/',             views.PolynymCreate.as_view(), name='polynym_create'),
    path('p/find/<slug:name>',       views.pfind_vu,                name='polynym_search'),
    path('p/find/',                  views.pfind_vu,                name='polynym_search'),
    path('polynym/area/<slug:area>', views.PolynymDetail.as_view(), name='polynyms_area'),
    path('polynym/src/<slug:src>',   views.PolynymDetail.as_view(), name='polynyms_src'),
    path('polynym/n/<int:n>',        views.PolynymDetail.as_view(), name='polynyms_n'),
    path('polynyms/',                views.PolynymTabler.as_view(), name='polynyms'),

    path('guessanym/use/<int:pk>/',        views.GuessanymUse.as_view(),    name='guessanym_use'), # GUESSANYM
    path('guessanym/<str:mark>/<int:pk>/', views.GuessanymDetail.as_view(), name='guessanym_mark'),
    path('guessanym/<str:what>/<int:pk>/', views.GuessanymDetail.as_view(), name='guessanym_detail'),
    path('guessanym/<str:what>/',          views.GuessanymDetail.as_view(), name='guessanym_detail'),
    path('guessanym/',                     views.GuessanymDetail.as_view(), name='guessanym_detail'),

    path('guessaquad/use/<int:pk>/<str:kind>/', views.GuessaquadUse.as_view(),    name='guessaquad_use'), # GUESSAQUAD
    path('guessaquad/use/<int:pk>/',            views.GuessaquadUse.as_view(),    name='guessaquad_use'),
    path('guessaquad/<str:mark>/<int:pk>/',     views.GuessaquadDetail.as_view(), name='guessaquad_mark'),
    path('guessaquad/<str:what>/<int:pk>/',     views.GuessaquadDetail.as_view(), name='guessaquad_detail'),
    path('guessaquad/<str:what>/',              views.GuessaquadDetail.as_view(), name='guessaquad_detail'),
    path('guessaquad/',                         views.GuessaquadDetail.as_view(), name='guessaquad_detail'),

    path('quadranym/',                  views.QuadranymDetail.as_view(), name='quadranym_detail'), # QUADRANYM
    path('quadranym/<int:pk>/',         views.QuadranymDetail.as_view(), name='quadranym_detail'),
    path('quadranym/update/<int:pk>',   views.QuadranymUpdate.as_view(), name='quadranym_update'),
    path('quadranym/update/<int:pk>/<str:kind>', views.QuadranymUpdate.as_view(), name='quadranym_update'),
    path('quadranym/delete/<int:pk>',   views.QuadranymDelete.as_view(), name='quadranym_delete'),
    path('quadranym/add/',              views.QuadranymCreate.as_view(), name='quadranym_create'),
    path('quadranym/add/<str:kind>',    views.QuadranymCreate.as_view(), name='quadranym_create'),
    path('q/find/<slug:name>',          views.qfind_vu,                  name='quadranym_search'),
    path('q/find/',                     views.qfind_vu,                  name='quadranym_search'),
    path('quadranyms/',                 views.QuadranymTabler.as_view(), name='quadranyms'),
    path('queue/',                      views.queue_add_vu,              name='queue'), # Q-QUEUE

    path('phrase/',                     views.PhraseDetail.as_view(), name='phrase_detail'), # PHRASE
    path('phrase/<int:pk>',             views.PhraseDetail.as_view(), name='phrase_detail'),
    path('phrase/update/<int:pk>',      views.PhraseUpdate.as_view(), name='phrase_update'),
    path('phrase/delete/<int:pk>',      views.PhraseDelete.as_view(), name='phrase_delete'),
    path('phrase/add/',                 views.PhraseCreate.as_view(), name='phrase_create'),

    path('fable/',                      views.FableDetail.as_view(), name='fable_detail'), # FABLE
    path('fable/<int:pk>',              views.FableDetail.as_view(), name='fable_detail'),
    path('fable/update/<int:pk>',       views.FableUpdate.as_view(), name='fable_update'),
    path('fable/delete/<int:pk>',       views.FableDelete.as_view(), name='fable_delete'),
    path('fable/add/',                  views.FableCreate.as_view(), name='fable_create'),

    path('tale/',                       views.TaleDetail.as_view(), name='tale_detail'), # TALE
    path('tale/<int:pk>',               views.TaleDetail.as_view(), name='tale_detail'),
    path('tale/add/',                   views.tale_add_vu,          name='tale_create'), # + pick Fable
    path('add/tale_menu/',              views.tale_menu_vu,         name='tale_menu'), # + maker (1)
    path('add/tale_list/',              views.tale_list_vu,         name='tale_list'), # + maker  2
    path('tale/delete/<int:pk>',        views.TaleDelete.as_view(), name='tale_delete'),
    path('save_tale/',                  views.tale_save_vu,         name='tale_save'),

    path('story/',                      views.StoryDetail.as_view(), name='story_detail'), # STORY
    path('story/<int:pk>',              views.StoryDetail.as_view(), name='story_detail'),
    path('story/add/',                  views.story_menu_vu,         name='story_create'), # + maker (1)
    path('add/story_pair/',             views.story_pair_vu,         name='story_pair'), # + maker  2
    path('add/story_list/',             views.story_list_vu,         name='story_list'), # + maker  3
    path('save_story/',                 views.story_save_vu,         name='story_save'),
    path('story/delete/<int:pk>',       views.StoryDelete.as_view(), name='story_delete'),

    path('polymap/',                    views.PolymapDetail.as_view(), name='polymap_detail'), # POLYMAP
    path('polymap/<int:pk>',            views.PolymapDetail.as_view(), name='polymap_detail'),
    path('polymap/add/',                views.polymap_add_vu,          name='polymap_create'),
    path('add/polymap2/',               views.polymap_add2_vu,         name='polymap_make'),
    path('save_polymap/',               views.polymap_save_vu,         name='polymap_save'),
    path('polymap/delete/<int:pk>',     views.PolymapDelete.as_view(), name='polymap_delete'),

    path('vectornym/',                  views.VectornymDetail.as_view(), name='vectornym_detail'), # VECTORNYM
    path('vectornym/<int:pk>',          views.VectornymDetail.as_view(), name='vectornym_detail'),
    path('vectornym/add/',              views.VectornymCreate.as_view(), name='vectornym_create'),
    path('vectornym/update/<int:pk>',   views.VectornymUpdate.as_view(), name='vectornym_update'),
    path('vectornym/delete/<int:pk>',   views.VectornymDelete.as_view(), name='vectornym_delete'),

    path('polyset/',                    views.PolysetDetail.as_view(), name='polyset_detail'), # POLYSET
    path('polyset/<int:pk>',            views.PolysetDetail.as_view(), name='polyset_detail'),
    path('polyset/update/<int:pk>',     views.PolysetUpdate.as_view(), name='polyset_update'),
    path('polyset/add/',                views.PolysetCreate.as_view(), name='polyset_create'),
    path('polyset/delete/<int:pk>',     views.PolysetDelete.as_view(), name='polyset_delete'),

    path('quadraset/',                  views.QuadrasetDetail.as_view(), name='quadraset_detail'), # QUADRASET
    path('quadraset/<int:pk>',          views.QuadrasetDetail.as_view(), name='quadraset_detail'),
    path('quadraset/update/<int:pk>',   views.QuadrasetUpdate.as_view(), name='quadraset_update'),
    path('quadraset/add/',              views.QuadrasetCreate.as_view(), name='quadraset_create'),
    path('quadraset/delete/<int:pk>',   views.QuadrasetDelete.as_view(), name='quadraset_delete'),

    path('polymath/',                   views.polymath_vu,    name='polymath'), # POLY MATH
    path('polytile/',                   views.polytile_vu,    name='polytile'),
    path('union/',                      views.union_vu,       name='union'),
    path('section/',                    views.section_vu,     name='section'),

    path('quadramath/',                 views.quadramath_vu,  name='quadramath'), # QUADRA MATH
    path('quadratile/<slug:name>',      views.quadratile_vu,  name='quadratile'),
    path('quadratile/',                 views.quadratile_vu,  name='quadratile'),

    path('thegist/',                    views.thegist_vu,     name='thegist'), # PLAY
    path('quizzection/',                views.quizzection_vu, name='quizzection'),
    path('polypuzzle/',                 views.polypuzzle_vu,  name='polypuzzle'),
    path('quadrazone/',                 views.quadrazone_vu,  name='quadrazone'),
    path('unquote/',                    views.unquote_vu,     name='unquote'),
    path('fame/<slug:game>',            views.fame_vu,        name='fame'),

    path('feel_fmk/',                   views.feel_fmk_vu,     name='feel_fmk'), # FEEL
    path('feel_mood/',                  views.feel_mood_vu,    name='feel_mood'),
    path('feel_polynym/',               views.feel_polynym_vu, name='feel_polynym'),
    path('feel_site/',                  views.feel_site_vu,    name='feel_site'),

    path('tell_phrase/',                views.tell_phrase_vu,  name='tell_phrase'), # TELL
    path('tell_tale/',                  views.tell_tale_vu,    name='tell_tale'),
    path('tell_verse/',                 views.tell_verse_vu,   name='tell_verse'),

    path('flip_fortune/',               views.flip_fortune_vu, name='flip_fortune'), # FLIP
    path('flip_quote/',                 views.flip_quote_vu,   name='flip_quote'),
    path('quote/<int:pk>',              views.flip_quote_vu,   name='quote'),
    path('flip_text/',                  views.flip_text_vu,    name='flip_text'),

    path('plot/',                       views.plot_vu,             name='plot'), # CHARTS
    path('plot/poly_area_rng/',         views.plot_poly_area_rng,  name='plot_poly_area_rng'),  # P-depths area: columnarea
    path('plot/poly_src_rng/',          views.plot_poly_src_rng,   name='plot_poly_src_rng'),   # P-depths src: columnarea
    path('plot/poly_mode_deps/',        views.plot_poly_mode_deps, name='plot_poly_mode_deps'), # P-depths mode: bar
    path('plot/poly_wordcloud/',        views.plot_poly_wordcloud, name='plot_poly_wordcloud'), # P.nyms: wordcloud
    path('plot/quad_wordcloud/',        views.plot_quad_wordcloud, name='plot_quad_wordcloud'), # Q.nyms: wordcloud
    path('plot/phra_wordcloud/',        views.plot_phra_wordcloud, name='plot_phra_wordcloud'), # Q.nyms: wordcloud
    path('plot/fabl_wordcloud/',        views.plot_fabl_wordcloud, name='plot_fabl_wordcloud'), # Q.nyms: wordcloud
    path('plot/poly_sectionym/',        views.plot_poly_sectionym, name='plot_poly_sectionym'), # SectionymP: wheel
    path('plot/poly_sectionet/',        views.plot_poly_sectionet, name='plot_poly_sectionet'), # SectionymP: networkgraph
    path('plot/quad_sectionet/',        views.plot_quad_sectionet, name='plot_quad_sectionet'), # SectionymQ: networkgraph
    path('plot/quad_polar/',            views.plot_quad_polar,     name='plot_quad_polar'),     # Quadranym: polar
    path('plot/poly_mode_dist/',        views.plot_poly_mode_dist, name='plot_poly_mode_dist'), # Polynym: modes } pie
    path('plot/quad_realm_dist/',       views.plot_quad_realm_dist,name='plot_quad_realm_dist'),# Quadranym: realms } pie
    #path('plot/tale_area_dist/',        views.plot_tale_area_dist, name='plot_tale_area_dist'), # Tale    areas }
    #path('plot/fabl_area_dist/',        views.plot_fabl_area_dist, name='plot_fabl_area_dist'), # Fable     "   }
    #path('plot/stor_area_dist/',        views.plot_stor_area_dist, name='plot_stor_area_dist'), # Story     "   }
    #path('plot/phra_area_dist/',        views.plot_phra_area_dist, name='plot_phra_area_dist'), # Phrase    "   } pie
    path('plot/poly_area_dist/',        views.plot_poly_area_dist, name='plot_poly_area_dist'), # Polynym   "   }
    path('plot/quad_area_dist/',        views.plot_quad_area_dist, name='plot_quad_area_dist'), # Quadranym "   }
    path('plot/pmap_area_dist/',        views.plot_pmap_area_dist, name='plot_pmap_area_dist'), # Polymap   "   }
    path('plot/tale_src_dist/',         views.plot_tale_src_dist,  name='plot_tale_src_dist'),  # Tale   sources }
    path('plot/fabl_src_dist/',         views.plot_fabl_src_dist,  name='plot_fabl_src_dist'),  # Fable     "    }
    path('plot/stor_src_dist/',         views.plot_stor_src_dist,  name='plot_stor_src_dist'),  # Story     "    }
    path('plot/phra_src_dist/',         views.plot_phra_src_dist,  name='plot_phra_src_dist'),  # Phrase    "    } pie
    path('plot/poly_src_dist/',         views.plot_poly_src_dist,  name='plot_poly_src_dist'),  # Polynym   "    }
    path('plot/quad_src_dist/',         views.plot_quad_src_dist,  name='plot_quad_src_dist'),  # Quadranym "    }
    path('plot/pmap_src_dist/',         views.plot_pmap_src_dist,  name='plot_pmap_src_dist'),  # Polymap   "    }
]
