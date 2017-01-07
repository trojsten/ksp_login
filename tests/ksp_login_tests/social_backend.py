from __future__ import unicode_literals
from social_core.backends.oauth import BaseOAuth2


class DummyTestingAuth1(BaseOAuth2):
    """Dummy social auth provider for testing purposes.

    This auth backend emulates an OAuth2 workflow.  It always redirects
    directly to the return URL instead of the provider's auth page.
    """
    name = 'test1'
    REDIRECT_STATE = False
    STATE_PARAMETER = False

    def auth_url(self):
        return self.get_redirect_uri()

    def get_user_details(self, *args, **kwargs):
        return {
            'username': 'koniiiik',
            'email': 'b@a.com',
            'first_name': 'Colleague',
            'last_name': 'Knuk',
        }

    def request_access_token(self, *args, **kwargs):
        return {'access_token': 'token'}

    def get_user_id(self, *args, **kwargs):
        return 'Testing UID #1'
