from django.utils.importlib import import_module
from django.shortcuts import redirect
from social.apps.django_app.utils import setting
from social.pipeline.partial import partial


@partial
def register_user(user, *args, **kwargs):
    """
    Pipeline function which redirects new users to the registration view.
    """
    if user is not None and user.is_authenticated():
        return None
    return redirect('account_register')
