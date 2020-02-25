from django.urls import path, include
from . import views

app_name = 'spin'
urlpatterns = [
    path('',                            views.index_vu),
    path('index.html',                  views.index_vu,                 name='home'),        # HOME
    path('accounts/',                   include('django.contrib.auth.urls')),                # AUTH
    path('signup/',                     views.SignUp.as_view()),                             # SIGNUP
    path('<str:com>/<int:pk>/vote/<str:io>/', views.CommonVote.as_view()),                   # VOTE
    path('user/<str:username>',         views.user_vu,                  name='user_detail'), # USER
    #path('wiz/',                        views.FormWizardView.as_view(), name='wiz'),

    path('polynym/',                    views.PolynymDetail.as_view(), name='polynym_detail'), # POLYNYM
    path('polynym/<int:pk>/',           views.PolynymDetail.as_view(), name='polynym_detail'),
    path('polynym/update/<int:pk>',     views.PolynymUpdate.as_view(), name='polynym_update'),
    path('polynym/delete/<int:pk>',     views.PolynymDelete.as_view(), name='polynym_delete'),
    path('polynym/add/',                views.PolynymCreate.as_view(), name='polynym_create'),
    path('polynym/area/<slug:area>',    views.PolynymDetail.as_view(), name='polynym_detail'), # area
    path('polynym/src/<slug:src>',      views.PolynymDetail.as_view(), name='polynym_detail'), # src
    path('polynym/n/<int:n>',           views.PolynymDetail.as_view(), name='polynym_detail'), # N-nyms
    path('polynyms/',                   views.PolynymList.as_view(),   name='polynym_list'),   # list
    path('polynyms/sort/',              views.PolynymTable.as_view(),  name='polynym_sort'),   # sort

    path('quadranym/',                  views.QuadranymDetail.as_view(), name='quadranym_detail'), # QUADRANYM
    path('quadranym/<int:pk>/',         views.QuadranymDetail.as_view(), name='quadranym_detail'),
    path('quadranym/update/<int:pk>',   views.QuadranymUpdate.as_view(), name='quadranym_update'),
    path('quadranym/delete/<int:pk>',   views.QuadranymDelete.as_view(), name='quadranym_delete'),
    path('quadranym/add/',              views.QuadranymCreate.as_view(), name='quadranym_create'),
    path('quadranym/add/<str:kind>',    views.QuadranymCreate.as_view(), name='quadranym_create'),
    path('quadranyms/',                 views.QuadranymList.as_view(),   name='quadranym_list'),   # list
    path('quadranyms/sort/',            views.QuadranymTable.as_view(),  name='quadranym_sort'),   # sort

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
    path('tale/add/',                   views.tale_add_vu,          name=''), # +
    path('add/tale2/',                  views.tale_a2d_vu,          name=''), # + pusher (A)
    path('add/tale2b/',                 views.tale_a2b_vu,          name=''), # + pusher  B
    path('tale/delete/<int:pk>',        views.TaleDelete.as_view(), name='tale_delete'),
    path('save_tale/',                  views.tale_save_vu,         name=''),

    path('queue/',                      views.queue_add_vu, name=''), # QUEUE

    path('story/',                      views.StoryDetail.as_view(), name='story_detail'), # STORY
    path('story/<int:pk>',              views.StoryDetail.as_view(), name='story_detail'),
    path('story/add/',                  views.story_add_vu,          name=''), # + pusher (A)
    path('add/storyb/',                 views.story_adb_vu,          name=''), # + pusher  B
    path('add/storyc/',                 views.story_adc_vu,          name=''), # + pusher  C
    path('save_story/',                 views.story_save_vu,         name=''),
    path('story/delete/<int:pk>',       views.StoryDelete.as_view(), name='story_delete'),

    path('polymap/',                    views.PolymapDetail.as_view(), name='polymap_detail'), # POLYMAP
    path('polymap/<int:pk>',            views.PolymapDetail.as_view(), name='polymap_detail'),
    path('polymap/add/',                views.polymap_add_vu,          name=''),
    path('add/polymap2/',               views.polymap_adn_vu,          name=''),
    path('save_polymap/',               views.polymap_save_vu,         name=''),
    path('polymap/delete/<int:pk>',     views.PolymapDelete.as_view(), name='polymap_delete'),

    path('vectornym/',                  views.VectornymDetail.as_view(), name='vectornym_detail'), # VECTORNYM
    path('vectornym/<int:pk>',          views.VectornymDetail.as_view(), name='vectornym_detail'),
    path('vectornym/add/',              views.vectornym_add_vu,          name=''),
    path('save_vectornym/',             views.vectornym_save_vu,         name=''),
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

    path('hyperq/<slug:name>',          views.hyperq_vu,      name=''), #  HYPER Q      slug:name
    path('hyperq/',                     views.hyperq_vu,      name=''),
    path('q/find/<slug:name>',          views.qfind_vu,       name=''), # Q-FIND        slug:name
    path('q/find/',                     views.qfind_vu,       name=''),
    path('p/find/<slug:name>',          views.pfind_vu,       name=''), # P-FIND        slug:name
    path('p/find/',                     views.pfind_vu,       name=''),
    path('union/',                      views.union_vu,       name=''), # UNIONYM
    path('section/',                    views.section_vu,     name=''), # SECTIONYM
    path('qontext/',                    views.qontext_vu,     name=''), # QONTEXT
    path('apolysis/',                   views.apolysis_vu,    name=''), # APOLYSIS
    path('polymath/',                   views.polymath_vu,    name=''), # POLYMATH
    path('polytile/',                   views.polytile_vu,    name=''), # POLYTILE
    path('polypuzl/',                   views.polypuzl_vu,    name=''), # POLYPUZZLE
    path('polyfame/',                   views.polyfame_vu,    name=''),
    path('emo/',                        views.emo_vu,         name=''), # EMONYM
    path('polykins/',                   views.polykins_vu,    name=''), # POLYKINS
    path('fmk/',                        views.fmk_vu,         name=''), # FUNMARRYKILL
    path('quizzection/',                views.quizzection_vu, name=''), # QUIZZECTION
    path('quizfame/',                   views.quizfame_vu,    name=''),
    path('qspin/',                      views.qspin_vu,       name=''), # EZ-SPIN
    path('fspin/',                      views.fspin_vu,       name=''), # TALESPIN
    path('mspin/',                      views.mspin_vu,       name=''), # SPINVERSE
    path('oraq/',                       views.oraq_vu,        name=''), # ORA Q
    path('unquote/',                    views.unquote_vu,     name=''), # UNQUOTE
    path('turnr/',                      views.turnr_vu,       name=''), # TURNR

    path('plot/',                       views.plot_vu,             name=''), # POLYPLOT:
    path('plot/poly_area_rng/',         views.plot_poly_area_rng,  name='plot_poly_area_rng'), # P-depths area: columnarea
    path('plot/poly_src_rng/',          views.plot_poly_src_rng,   name='plot_poly_src_rng'),  # P-depths src: columnarea
    path('plot/poly_mode_deps/',        views.plot_poly_mode_deps, name='plot_poly_mode_deps'),# P-depths mode: bar
    path('plot/poly_wordcloud/',        views.plot_poly_wordcloud, name='plot_poly_wordcloud'),# P.nyms: wordcloud
    path('plot/quad_wordcloud/',        views.plot_quad_wordcloud, name='plot_quad_wordcloud'),# Q.nyms: wordcloud
    path('plot/phra_wordcloud/',        views.plot_phra_wordcloud, name='plot_phra_wordcloud'),# Q.nyms: wordcloud
    path('plot/fabl_wordcloud/',        views.plot_fabl_wordcloud, name='plot_fabl_wordcloud'),# Q.nyms: wordcloud
    path('plot/poly_sectionym/',        views.plot_poly_sectionym, name='plot_poly_sectionym'),# SectionymP: wheel
    path('plot/poly_sectionet/',        views.plot_poly_sectionet, name='plot_poly_sectionet'),# SectionymP: networkgraph
    path('plot/quad_sectionet/',        views.plot_quad_sectionet, name='plot_quad_sectionet'),# SectionymQ: networkgraph
    path('plot/quad_polar/',            views.plot_quad_polar,     name='plot_quad_polar'),    # Quadranym: polar
    path('plot/poly_mode_dist/',        views.plot_poly_mode_dist, name='plot_poly_mode_dist'),# Polynym: modes } pie
    path('plot/quad_realm_dist/',       views.plot_quad_realm_dist,name='plot_quad_realm_dist'),# Quadranym: realms } pie
    path('plot/tale_area_dist/',        views.plot_tale_area_dist, name='plot_tale_area_dist'),# Tale    areas }
    path('plot/fabl_area_dist/',        views.plot_fabl_area_dist, name='plot_fabl_area_dist'),# Fable     "   }
    path('plot/stor_area_dist/',        views.plot_stor_area_dist, name='plot_stor_area_dist'),# Story     "   }
    path('plot/phra_area_dist/',        views.plot_phra_area_dist, name='plot_phra_area_dist'),# Phrase    "   } pie
    path('plot/poly_area_dist/',        views.plot_poly_area_dist, name='plot_poly_area_dist'),# Polynym   "   }
    path('plot/quad_area_dist/',        views.plot_quad_area_dist, name='plot_quad_area_dist'),# Quadranym "   }
    path('plot/pmap_area_dist/',        views.plot_pmap_area_dist, name='plot_pmap_area_dist'),# Polymap   "   }
    path('plot/tale_src_dist/',         views.plot_tale_src_dist,  name='plot_tale_src_dist'),# Tale   sources }
    path('plot/fabl_src_dist/',         views.plot_fabl_src_dist,  name='plot_fabl_src_dist'),# Fable     "    }
    path('plot/stor_src_dist/',         views.plot_stor_src_dist,  name='plot_stor_src_dist'),# Story     "    }
    path('plot/phra_src_dist/',         views.plot_phra_src_dist,  name='plot_phra_src_dist'),# Phrase    "    } pie
    path('plot/poly_src_dist/',         views.plot_poly_src_dist,  name='plot_poly_src_dist'),# Polynym   "    }
    path('plot/quad_src_dist/',         views.plot_quad_src_dist,  name='plot_quad_src_dist'),# Quadranym "    }
    path('plot/pmap_src_dist/',         views.plot_pmap_src_dist,  name='plot_pmap_src_dist'),# Polymap   "    }
]  #path('plot/poly_tilemap/',          views.plot_poly_tilemap,   name='plot_poly_tilemap'), # P-depths mode: tilemap,lol
