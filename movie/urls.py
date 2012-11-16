from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    #url(r'rec_list/','movie.views.rec_list'),
    url(r'accounts/register', 'movie.views.feed_rec'),
    url(r'feed_rec/','movie.views.feed_rec'),
    url(r'get_rec/','movie.views.get_rec'),
    url(r'myratings/','movie.views.myratings'),
    url(r'detail/(?P<pk>\w+)/','movie.views.detail'),
    # Examples:
    # url(r'^$', 'web.views.home', name='home'),
    # url(r'^web/', include('web.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
