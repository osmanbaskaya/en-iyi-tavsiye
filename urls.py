from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from iface.registerviews import UserProfile
from iface.registerviews import UserProfileUpdate

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve'),

    url(r'^avatars/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': '/var/en-iyi-tavsiye/iface/avatars'}),
    url(r'^$', 'iface.views.log_in'),
    url(r'^login/$', 'iface.views.log_in'),
    url(r'logout/', 'iface.views.exit'),
    url(r'movie', include('movie.urls')),
    url(r'imdbdata', include('imdbdata.urls')),
    url(r'experimental', include('experimental.urls')),
    url(r'book', include('book.urls')),
    url(r'^accounts', include('iface.urls')),
    url(r'myprofile',UserProfileUpdate.as_view(),name='userprofile_update'),
    #url(r'accounts/', include('registration.backends.default.urls')),

    #url(r'book', include('book.urls'),
    # Examples:
    # url(r'^$', 'web.views.home', name='home'),
    # url(r'^web/', include('web.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
#urlpatterns += staticfiles_urlpatterns()
