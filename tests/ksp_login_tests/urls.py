from __future__ import unicode_literals

from django.conf.urls import include, url
from django.shortcuts import render


def hello_world(request):
    """
    Trivial view for testing purposes.
    """
    return render(request, 'base.html')


urlpatterns = [
    url(r'^$', hello_world, name='hello_world'),
    url(r'^account/', include('ksp_login.urls')),
]
