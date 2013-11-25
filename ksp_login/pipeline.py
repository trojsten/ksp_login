from django.utils.importlib import import_module
from django.shortcuts import redirect
from social.apps.django_app.utils import setting
from social.pipeline.partial import partial


@partial
def register_user(request, user, *args, **kwargs):
    """
    Pipeline function which redirects new users to the registration view.
    """
    if request.user.is_authenticated() or user:
        return None
    return redirect('account_register')
