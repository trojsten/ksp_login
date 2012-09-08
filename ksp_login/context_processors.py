import re

from social_auth.utils import setting
from social_auth.models import UserSocialAuth


def prepare_regexes(providers):
    """
    Convenience function which compiles the recognition regular
    expressions in provider entries for backends that need it. This works
    in place, which means the regex should only be compiled once per
    process.
    """
    for provider in providers:
        if ('compiled_recognition_re' not in provider and
            'recognition_re' in provider):
            provider['compiled_recognition_re'] = re.compile(provider['recognition_re'])


def get_authentication_providers(request, short=False):
    """
    Returns a list of available authentication providers based on the
    AUTHENTICATION_PROVIDERS setting. Each provider is represented as a
    dictionary containing the social_auth backend name, display name and
    a list of account associations to the provider for the currently
    logged in user.
    """
    providers = setting('AUTHENTICATION_PROVIDERS', tuple())
    if short:
        return providers[:setting('AUTHENTICATION_PROVIDERS_BRIEF')]

    prepare_regexes(providers)

    # Create a copy of each dictionary since we add the lists of
    # associated accounts to them.
    providers = [dict(provider) for provider in providers]

    # Gather associated accounts.
    associations = (request.user.is_authenticated() and
                    UserSocialAuth.get_social_auth_for_user(request.user) or
                    [])
    for assoc in associations:
        for provider in providers:
            if (provider['backend'] == assoc.provider and
                (provider['backend'] != 'openid' or
                 provider['compiled_recognition_re'].search(assoc.uid) is not None)):
                provider.setdefault('associations', []).append(assoc)
                break

    # Finally we reorder the list to put those with associations to the
    # beginning.
    return ([provider for provider in providers if
             len(provider.setdefault('associations', [])) > 0] +
            [provider for provider in providers if
             len(provider['associations']) == 0])


def authentication_providers(request):
    """
    Returns the full list of authentication providers as the social_auth
    context variable.
    """
    return {'social_auth': get_authentication_providers(request)}


def authentication_providers_short(request):
    """
    Returns the short list of authentication providers for use in a login
    widget as the social_auth context variable.
    """
    return {'social_auth': get_authentication_providers(request, short=True)}
