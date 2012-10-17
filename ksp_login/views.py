from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (login as auth_login,
    password_change)
from django.contrib.auth.forms import SetPasswordForm
from social_auth.models import UserSocialAuth
from social_auth.utils import setting
from social_auth.views import disconnect as social_auth_disconnect
from ksp_login import SOCIAL_AUTH_PARTIAL_PIPELINE_KEY
from ksp_login.context_processors import login_providers
from ksp_login.forms import (KspUserCreationForm, PasswordChangeForm,
    UserProfileForm)


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


def register(request, creation_form=KspUserCreationForm):
    """
    As the name suggests, registers a new user.

    Can replace the create_user function in the SOCIAL_AUTH pipeline
    (through ksp_login.pipeline.register_user, with the corresponding
    save_status_to_session, of course) to make it possible for the user to
    pick a username.
    """
    if request.user.is_authenticated():
        return redirect('account_info')
    try:
        pipeline_state = request.session[setting('SOCIAL_AUTH_PARTIAL_PIPELINE_KEY',
                                                 SOCIAL_AUTH_PARTIAL_PIPELINE_KEY)]
        backend = pipeline_state['backend']
        pipeline_state = pipeline_state['kwargs']
        standalone = False
    except KeyError:
        standalone = True
    if request.method == "POST":
        form = creation_form(request.POST, request=request)
        if form.is_valid():
            user = form.save()
            if standalone:
                return redirect('account_login')
            pipeline_state['user'] = user
            request.session.modified = True
            print request.session.items()
            return redirect('socialauth_complete', backend=backend)
    else:
        form = creation_form(request=request)

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


@login_required
def password(request):
    """
    Sets, changes or removes the currently logged in user's passwords,
    depending on whether they have any social account associations.
    """
    has_assoc = UserSocialAuth.get_social_auth_for_user(request.user).count()
    if request.user.has_usable_password():
        def form(*args, **kwargs):
            return PasswordChangeForm(not has_assoc, *args, **kwargs)
    else:
        form = SetPasswordForm
    return password_change(request,
                           post_change_redirect=reverse('account_info'),
                           password_change_form=form,
                           template_name='ksp_login/password.html')


@login_required
def settings(request, settings_form=UserProfileForm):
    """
    Presents the user a form with their settings, basically the register
    form minus username minus password.
    """
    if request.method == "POST":
        form = settings_form(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('account_info')
    else:
        form = settings_form(user=request.user)

    return render(request, 'ksp_login/settings.html', {
        'form': form,
    })
