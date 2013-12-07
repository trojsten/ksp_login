from __future__ import unicode_literals

from django.shortcuts import render
from django.conf.urls.defaults import patterns, include, url
from django.core.urlresolvers import reverse_lazy


def hello_world(request):
    """
    Trivial view for testing purposes.
    """
    return render(request, 'base.html')


urlpatterns = patterns('',
    url(r'^$', hello_world, name='hello_world'),
    url(r'^account/', include('ksp_login.urls')),
)
