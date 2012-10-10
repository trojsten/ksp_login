import re

from social_auth.backends import get_backends
from social_auth.utils import setting
from social_auth.models import UserSocialAuth


DEFAULT_AUTHENTICATION_PROVIDERS_BRIEF = 3


def get_login_providers(request, short=False):
    """
    Returns a list of available login providers based on the
    AUTHENTICATION_BACKENDS setting. Each provider is represented as a
    dictionary containing the social_auth Auth class, display name and a
    list of account associations to the provider for the currently logged
    in user.
    """
    def extract_backend_data(name, klass):
        """
        Helper function which extracts information useful for use in
        templates from SocialAuth subclasses and returns it as a
        dictionary.
        """
        return {
            'name': name,
            'required_field': klass.AUTH_BACKEND.REQUIRED_FIELD_NAME,
            'required_field_verbose': klass.AUTH_BACKEND.REQUIRED_FIELD_VERBOSE_NAME,
            'associations': [],
        }

    providers = [extract_backend_data(name, auth)
                 for name, auth in get_backends().items()]
    if short:
        return providers[:setting('AUTHENTICATION_PROVIDERS_BRIEF',
                                  DEFAULT_AUTHENTICATION_PROVIDERS_BRIEF)]
    associations = (request.user.is_authenticated() and
                    UserSocialAuth.get_social_auth_for_user(request.user) or
                    [])
    for assoc in associations:
        for provider in providers:
            if provider['name'] == assoc.provider:
                provider['associations'].append(assoc)
                break

    # Finally we reorder the list to put those with associations to the
    # beginning.
    return ([provider for provider in providers if
             len(provider['associations']) > 0] +
            [provider for provider in providers if
             len(provider['associations']) == 0])


def login_providers(request):
    """
    Returns the full list of login providers as the social_auth context
    variable.
    """
    return {'login_providers': get_login_providers(request)}


def login_providers_short(request):
    """
    Returns the short list of login providers for use in a login widget as
    the social_auth context variable.
    """
    return {'login_providers_short': get_login_providers(request, short=True)}
