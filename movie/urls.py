from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    #url(r'rec_list/','movie.views.rec_list'),
    url(r'accounts/register', 'movie.views.feedrec'),
    url(r'feedrec/','movie.views.feedrec'),
    url(r'get_rec/','movie.views.get_rec'),
    url(r'unfollow/','movie.views.unfollow'),
    url(r'follow/','movie.views.follow'),
    url(r'train/','movie.views.train'),
    url(r'home/','movie.views.home'),
    url(r'userrec/','movie.views.userrec'),
    url(r'profile/','movie.views.profile'),
    url(r'rate/','movie.views.rate'),
    url(r'reclist','movie.views.reclist'),
    url(r'search/','movie.views.search'),
    url(r'detail/(?P<pk>\w+)/','movie.views.detail'),
    # Examples:
    # url(r'^$', 'web.views.home', name='home'),
    # url(r'^web/', include('web.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
