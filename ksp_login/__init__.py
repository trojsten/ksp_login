from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext_lazy as _


SOCIAL_AUTH_PARTIAL_PIPELINE_KEY = 'partial_pipeline'


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
    backends.BACKENDSCACHE = SortedDict()

__activate_social_auth_monkeypatch()
