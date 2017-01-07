from django.utils.translation import ugettext_lazy as _
from social_core.backends.open_id import OpenIdAuth
from social_core.exceptions import AuthMissingParameter


class UsernameBasedOpenIdAuth(OpenIdAuth):
    """
    OpenID authentication that determines the URL based on a predefined
    template and a username. Corresponding backends are supposed to
    define the URL_TEMPLATE class attribute which is an old-style format
    string.
    """
    def openid_url(self):
        """
        Returns the URL composed of a template with the specified username
        substituted.
        """
        try:
            return (self.URL_TEMPLATE %
                    self.data.get(self.REQUIRED_FIELD_NAME))
        except KeyError:
            raise AuthMissingParameter(self,
                                       self.REQUIRED_FIELD_VERBOSE_NAME)


class LaunchpadAuth(UsernameBasedOpenIdAuth):
    name = 'launchpad'
    URL_TEMPLATE = 'https://launchpad.net/~%s'
    REQUIRED_FIELD_NAME = 'openid_lp_username'
    REQUIRED_FIELD_VERBOSE_NAME = _('Launchpad username')


class MyOpenIdAuth(UsernameBasedOpenIdAuth):
    name = 'myopenid'
    URL_TEMPLATE = 'https://%s.myopenid.com/'
    REQUIRED_FIELD_NAME = 'myopenid_username'
    REQUIRED_FIELD_VERBOSE_NAME = _('MyOpenID username')
