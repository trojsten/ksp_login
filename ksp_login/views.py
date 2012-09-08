from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from ksp_login.context_processors import authentication_providers

def login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('account_info'))
    return render(request, 'ksp_login/login.html',
                  authentication_providers(request))

@login_required
def info(request):
    return render(request, 'ksp_login/info.html',
                  authentication_providers(request))

def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse('account_info'))
