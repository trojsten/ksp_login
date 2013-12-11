from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse_lazy
from django.views.generic.base import RedirectView

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
    url(r'', include('social.apps.django_app.urls', namespace='social')),
    url(r'^settings/', RedirectView.as_view(url=reverse_lazy('account_settings'))),
)
