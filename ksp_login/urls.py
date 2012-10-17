from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('ksp_login.views',
    url(r'^login/$', 'login', name='account_login'),
    url(r'^$', 'info', name='account_info'),
    url(r'^logout/$', 'logout', name='account_logout'),
    url(r'^register/$', 'register', name='account_register'),
    url(r'^disconnect/(?P<backend>[^/]+)/(?P<association_id>[^/]+)/$',
        'disconnect', name='account_disconnect'),
    url(r'^password/$', 'password', name='account_password'),
    url(r'^settings/$', 'settings', name='account_settings'),
)

urlpatterns += patterns('',
    url(r'', include('social_auth.urls')),
)
