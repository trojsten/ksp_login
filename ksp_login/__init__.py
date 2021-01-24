__version__ = '0.6.2'
__version_info__ = tuple(map(int, __version__.split('.')))

from django.utils.translation import ugettext_lazy as _


def __activate_social_auth_monkeypatch():
    from social_core.backends.base import BaseAuth
    from social_core.backends.open_id import (OPENID_ID_FIELD, OpenIdAuth)
    from social_core.backends.livejournal import LiveJournalOpenId

    BaseAuth.REQUIRED_FIELD_NAME = None
    BaseAuth.REQUIRED_FIELD_VERBOSE_NAME = None

    OpenIdAuth.REQUIRED_FIELD_NAME = OPENID_ID_FIELD
    OpenIdAuth.REQUIRED_FIELD_VERBOSE_NAME = _('OpenID identity')

    LiveJournalOpenId.REQUIRED_FIELD_NAME = 'openid_lj_user'
    LiveJournalOpenId.REQUIRED_FIELD_VERBOSE_NAME = _('LiveJournal username')


__activate_social_auth_monkeypatch()
