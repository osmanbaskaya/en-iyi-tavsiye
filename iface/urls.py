#! /usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Osman Baskaya"

from django.conf.urls.defaults import patterns, include, url
from registration.views import register
from iface.registerviews import RegistrationFormZ

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    #     url(r'register/$',register,  {'form_class' : RegistrationFormZ}, 
    #        name= 'registration_register'),
    url(r'register/$', 'iface.views.create_account'),
    #url(r'register/activate/$', 'iface.views.create_account'),
    #url(r'accounts/', include('registration.backends.default.urls')),

    #url(r'book', include('book.urls'),
    # Examples:
    # url(r'^$', 'web.views.home', name='home'),
    # url(r'^web/', include('web.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
)

