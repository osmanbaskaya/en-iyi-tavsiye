from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
import os
admin.autodiscover()

context = os.path.basename(os.path.dirname(os.path.realpath(__file__)))
urlpatterns = patterns('',
    url(r'accounts/register', '%s.views.feedrec'%context),
    url(r'feedrec/','%s.views.feedrec'%context),
    url(r'get_rec/','%s.views.get_rec'%context),
    url(r'unfollow/','%s.views.unfollow'%context),
    url(r'follow/','%s.views.follow'%context),
    url(r'fetch/','%s.views.fetch'%context),
    url(r'home/','%s.views.home'%context),
    url(r'userrec/','%s.views.userrec'%context),
    url(r'profile/','%s.views.profile'%context),
    url(r'rate/','%s.views.rate'%context),
    url(r'reclist','%s.views.reclist'%context),
    url(r'search/','%s.views.search'%context),
    url(r'detail/(?P<pk>\w+)/','%s.views.detail'%context),
    # Examples:
    # url(r'^$', 'web.views.home', name='home'),
    # url(r'^web/', include('web.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
