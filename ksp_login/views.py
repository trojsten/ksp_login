from collections import OrderedDict
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from ksp_login.context_processors import login_providers

def login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('account_info'))
    return render(request, 'ksp_login/login.html',
                  login_providers(request))

@login_required
def info(request):
    return render(request, 'ksp_login/info.html',
                  login_providers(request))

def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse('account_info'))


def __activate_social_auth_monkeypatch():
    from social_auth.backends import (OPENID_ID_FIELD, SocialAuthBackend,
        OpenIDBackend)
    from social_auth.backends.contrib.livejournal import (
        LIVEJOURNAL_USER_FIELD, LiveJournalBackend)
    from social_auth.backends.yahoo import YahooBackend
    from social_auth.backends.google import GoogleBackend
    from social_auth.backends.contrib.yandex import YandexBackend
    from social_auth import backends

    SocialAuthBackend.REQUIRED_FIELD_NAME = None
    SocialAuthBackend.REQUIRED_FIELD_VERBOSE_NAME = None

    OpenIDBackend.REQUIRED_FIELD_NAME = OPENID_ID_FIELD
    OpenIDBackend.REQUIRED_FIELD_VERBOSE_NAME = _('OpenID identity')

    LiveJournalBackend.REQUIRED_FIELD_NAME = LIVEJOURNAL_USER_FIELD
    LiveJournalBackend.REQUIRED_FIELD_VERBOSE_NAME = _('LiveJournal username')

    # Reset to None in those OpenID backends where nothing is required.
    GoogleBackend.REQUIRED_FIELD_NAME = None
    GoogleBackend.REQUIRED_FIELD_VERBOSE_NAME = None
    YahooBackend.REQUIRED_FIELD_NAME = None
    YahooBackend.REQUIRED_FIELD_VERBOSE_NAME = None
    YandexBackend.REQUIRED_FIELD_NAME = None
    YandexBackend.REQUIRED_FIELD_VERBOSE_NAME = None

    # We replace the regular dict in social_auth.backends.BACKENDSCACHE
    # with an OrderedDict in order to remember the order in which they
    # were imported based on settings.AUTHENTICATION_BACKENDS.
    backends.BACKENDSCACHE = OrderedDict()

__activate_social_auth_monkeypatch()
