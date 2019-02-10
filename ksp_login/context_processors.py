from social_core.backends.base import BaseAuth
from social_core.utils import module_member

from .utils import setting

DEFAULT_AUTHENTICATION_PROVIDERS_BRIEF = 3


def get_login_providers(request, short=False):
    """
    Returns a list of available login providers based on the
    AUTHENTICATION_BACKENDS setting. Each provider is represented as a
    dictionary containing the backend name, name of required parameter if
    required and its verbose name.
    """
    def extract_backend_data(klass):
        """
        Helper function which extracts information useful for use in
        templates from SocialAuth subclasses and returns it as a
        dictionary.
        """
        return {
            'name': klass.name,
            'required_field': klass.REQUIRED_FIELD_NAME,
            'required_field_verbose': klass.REQUIRED_FIELD_VERBOSE_NAME,
        }

    backends = (module_member(auth_backend) for auth_backend in setting('AUTHENTICATION_BACKENDS'))
    providers = [extract_backend_data(backend) for backend in backends if issubclass(backend, BaseAuth)]
    if short:
        return providers[:setting('AUTHENTICATION_PROVIDERS_BRIEF',
                                  DEFAULT_AUTHENTICATION_PROVIDERS_BRIEF)]
    return providers


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


def login_providers_both(request):
    """
    Returns both the short and the long list of login providers.
    """
    return {
        'login_providers': get_login_providers(request),
        'login_providers_short': get_login_providers(request, short=True),
    }
