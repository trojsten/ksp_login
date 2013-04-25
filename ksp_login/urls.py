from django.conf.urls.defaults import patterns, include, url
from django.core.urlresolvers import reverse_lazy

urlpatterns = patterns('ksp_login.views',
    url(r'^login/$', 'login', name='account_login'),
    url(r'^$', 'settings', name='account_settings'),
    url(r'^logout/$', 'logout', name='account_logout'),
    url(r'^register/$', 'register', name='account_register'),
    url(r'^disconnect/(?P<backend>[^/]+)/(?P<association_id>[^/]+)/$',
        'disconnect', name='account_disconnect'),
    url(r'^password/$', 'password', name='account_password'),
)

urlpatterns += patterns('',
    url(r'', include('social_auth.urls')),
    url(r'^settings/', 'django.views.generic.simple.redirect_to',
        {'url': reverse_lazy('account_settings')}),
)
