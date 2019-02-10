from django.conf import settings
from social_django.utils import load_strategy, setting_name


def get_partial_pipeline(request):
    """
    """
    token = request.session.get('partial_pipeline_token')
    if not token:
        return None
    strategy = load_strategy(request)
    return strategy.partial_load(token)


def setting(name, default=None):
    try:
        return getattr(settings, setting_name(name))
    except AttributeError:
        return getattr(settings, name, default)
