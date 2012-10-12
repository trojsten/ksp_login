from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login as auth_login
from social_auth.models import UserSocialAuth
from social_auth.utils import setting
from social_auth.views import disconnect as social_auth_disconnect
from ksp_login.context_processors import login_providers
from ksp_login.forms import KspUserCreationForm


def login(request):
    if request.user.is_authenticated():
        return redirect('account_info')
    return auth_login(request, template_name='ksp_login/login.html',
                      extra_context=login_providers(request))


@login_required
def info(request):
    context = login_providers(request)
    context['account_associations'] = UserSocialAuth.get_social_auth_for_user(request.user)
    return render(request, 'ksp_login/info.html', context)


def logout(request):
    auth_logout(request)
    return redirect('account_info')


def register(request):
    """
    As the name suggests, registers a new user.

    Can replace the create_user function in the SOCIAL_AUTH pipeline
    (through ksp_login.pipeline.register_user, with the corresponding
    save_status_to_session, of course) to make it possible for the user to
    pick a username.
    """
    try:
        pipeline_state = request.session[setting('SOCIAL_AUTH_PARTIAL_PIPELINE_KEY',
                                                 'partial_pipeline')]
        backend = pipeline_state['backend']
        pipeline_state = pipeline_state['kwargs']
        standalone = False
    except KeyError:
        standalone = True
    if request.method == "POST":
        form = KspUserCreationForm(standalone, request.POST)
        if form.is_valid():
            user = form.save()
            if standalone:
                return redirect('account_login')
            pipeline_state['user'] = user
            request.session.modified = True
            return redirect('socialauth_complete', backend=backend)
    else:
        initial_data = None if standalone else {
            'username': pipeline_state['username'],
            'first_name': pipeline_state['details']['first_name'],
            'last_name': pipeline_state['details']['last_name'],
            'email': pipeline_state['details']['email'],
        }
        form = KspUserCreationForm(initial=initial_data,
                                   password_required=standalone)

    return render(request, "ksp_login/registration.html", {
        'form': form,
    })


@login_required
def disconnect(request, backend, association_id):
    """
    If the user has at least one other social account association or a
    valid password, disconnects the given social account, otherwise asks
    the user to set up a password before proceeding.
    """
    associations = UserSocialAuth.get_social_auth_for_user(request.user)
    has_assoc = associations.exclude(id=association_id).count()
    has_pass = request.user.has_usable_password()
    if has_assoc or has_pass:
        return social_auth_disconnect(request, backend, association_id)
    return render(request, 'ksp_login/invalid_disconnect.html')
