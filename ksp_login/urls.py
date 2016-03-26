from django.conf.urls import include, url
from django.core.urlresolvers import reverse_lazy
from django.views.generic.base import RedirectView

from ksp_login import views


urlpatterns = [
    url(r'^login/$', views.login, name='account_login'),
    url(r'^$', views.settings, name='account_settings'),
    url(r'^logout/$', views.logout, name='account_logout'),
    url(r'^register/$', views.register, name='account_register'),
    url(r'^disconnect/(?P<backend>[^/]+)/(?P<association_id>[^/]+)/$',
        views.disconnect, name='account_disconnect'),
    url(r'^password/$', views.password, name='account_password'),

    url(r'', include('social.apps.django_app.urls', namespace='social')),
    url(r'^settings/', RedirectView.as_view(url=reverse_lazy('account_settings'))),
]
