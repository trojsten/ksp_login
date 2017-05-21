from social_django.utils import load_strategy


def get_partial_pipeline(request):
    """
    """
    token = request.session.get('partial_pipeline_token')
    if not token:
        return None
    strategy = load_strategy(request)
    return strategy.partial_load(token)
