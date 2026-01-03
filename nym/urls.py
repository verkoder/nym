#!/usr/bin/env python
# encoding: utf-8
'''
urls.py -- Nymology project url patterns
'''
#import debug_toolbar
from django.contrib import admin
from django.urls import include, path
from django.contrib.auth.decorators import login_required

admin.autodiscover()
admin.site.login = login_required(admin.site.login)
urlpatterns = [
    path('', include('spin.urls')),
    path('admin/', admin.site.urls),
    #path('__debug__/', include(debug_toolbar.urls)), # dEBUG TOOLBAR
]
