from django.utils.translation import ugettext_lazy as _
from social_auth.backends import OpenIDBackend, OpenIdAuth
from social_auth.backends.exceptions import AuthMissingParameter


class UsernameBasedOpenIdAuth(OpenIdAuth):
    """
    OpenID authentication that determines the URL based on a predefined
    template and an username. Corresponding backends are supposed to
    define the URL_TEMPLATE class attribute which is an old-style format
    string.
    """
    def openid_url(self):
        """
        Returns the URL composed of a template with the specified username
        substituted.
        """
        try:
            return (self.AUTH_BACKEND.URL_TEMPLATE %
                    self.data.get(self.AUTH_BACKEND.REQUIRED_FIELD_NAME))
        except KeyError:
            raise AuthMissingParameter(self,
                                       self.AUTH_BACKEND.REQUIRED_FIELD_VERBOSE_NAME)


class LaunchpadBackend(OpenIDBackend):
    name = 'launchpad'
    URL_TEMPLATE = 'https://launchpad.net/~%s'
    REQUIRED_FIELD_NAME = 'openid_lp_username'
    REQUIRED_FIELD_VERBOSE_NAME = _('Launchpad username')


class LaunchpadAuth(UsernameBasedOpenIdAuth):
    AUTH_BACKEND = LaunchpadBackend


class MyOpenIdBackend(OpenIDBackend):
    name = 'myopenid'
    URL_TEMPLATE = 'https://%s.myopenid.com/'
    REQUIRED_FIELD_NAME = 'myopenid_username'
    REQUIRED_FIELD_VERBOSE_NAME = _('MyOpenID username')

class MyOpenIdAuth(UsernameBasedOpenIdAuth):
    AUTH_BACKEND = MyOpenIdBackend


BACKENDS = {
    'launchpad': LaunchpadAuth,
    'myopenid': MyOpenIdAuth,
}
