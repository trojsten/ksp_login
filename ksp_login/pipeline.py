from django.shortcuts import redirect
from social_core.pipeline.partial import partial


@partial
def register_user(user, *args, **kwargs):
    """
    Pipeline function which redirects new users to the registration view.
    """
    if user is not None and user.is_authenticated:
        return None
    return redirect('account_register')
