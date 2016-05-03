from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.views import (
    login as auth_login, logout as auth_logout, password_change,
)
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render, resolve_url
from django.utils.http import is_safe_url
from django.utils.translation import ugettext_lazy as _

from social.apps.django_app.default.models import UserSocialAuth
from social.apps.django_app.utils import setting
from social.apps.django_app.views import disconnect as social_disconnect

from ksp_login import SOCIAL_AUTH_PARTIAL_PIPELINE_KEY
from ksp_login.context_processors import login_providers
from ksp_login.forms import (
    get_profile_forms, KspUserCreationForm, PasswordChangeForm,
    UserProfileForm,
)


def login(request):
    # TODO: Remove this in favor of redirect_authenticated_user once we
    # drop support for Django<1.10.
    if request.user.is_authenticated():
        next_page = request.GET.get('next', request.POST.get('next', ''))
        if not is_safe_url(url=next_page, host=request.get_host()):
            next_page = resolve_url(setting('LOGIN_REDIRECT_URL'))
        return HttpResponseRedirect(next_page)
    return auth_login(request, template_name='ksp_login/login.html',
                      extra_context=login_providers(request))


def logout(request):
    response = auth_logout(request, next_page='/')
    messages.success(request, _("Logout successful"))
    return response


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
        return social_disconnect(request=request, backend=backend,
                                 association_id=association_id)
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
                           post_change_redirect=reverse('account_settings'),
                           password_change_form=form,
                           template_name='ksp_login/password.html')


def register(request, creation_form=KspUserCreationForm):
    """
    As the name suggests, registers a new user.

    Can replace the create_user function in the SOCIAL_AUTH pipeline
    (through ksp_login.pipeline.register_user, with the corresponding
    save_status_to_session, of course) to make it possible for the user to
    pick a username.

    Also presents additional app-specific forms listed in the
    KSP_LOGIN_PROFILE_FORMS setting to the user.
    """
    if request.user.is_authenticated():
        return redirect('account_settings')
    try:
        pipeline_state = request.session[setting('SOCIAL_AUTH_PARTIAL_PIPELINE_KEY',
                                                 SOCIAL_AUTH_PARTIAL_PIPELINE_KEY)]
        backend = pipeline_state['backend']
        pipeline_state = pipeline_state['kwargs']
        standalone = False
    except KeyError:
        standalone = True

    form_classes = [creation_form] + get_profile_forms()

    if request.method == "POST":
        forms = [form(request.POST, request=request)
                 for form in form_classes]
        if all(form.is_valid() for form in forms):
            user = forms[0].save()
            for form in forms[1:]:
                form.set_user(user)
                form.save()
            if standalone:
                return redirect('account_login')
            pipeline_state['user'] = user.id
            # This ensures the top-level session dict changes, otherwise
            # our changes in pipeline_state might not get stored.
            request.session.setdefault('ksp_login_dummy_key', 0)
            request.session['ksp_login_dummy_key'] += 1
            return redirect('social:complete', backend=backend)
    else:
        forms = [form(request=request) for form in form_classes]

    return render(request, "ksp_login/registration.html", {
        'forms': forms,
    })


@login_required
def settings(request, settings_form=UserProfileForm):
    """
    Presents the user a form with their settings, basically the register
    form minus username minus password.

    Also presents additional app-specific forms listed in the
    KSP_LOGIN_PROFILE_FORMS setting to the user.
    """
    form_classes = [settings_form] + get_profile_forms()

    if request.method == "POST":
        forms = [form(request.POST, user=request.user)
                 for form in form_classes]
        if all(form.is_valid() for form in forms):
            for form in forms:
                form.save()
            return redirect('account_settings')
    else:
        forms = [form(user=request.user) for form in form_classes]

    return render(request, 'ksp_login/settings.html', {
        'account_associations': UserSocialAuth.get_social_auth_for_user(request.user),
        'forms': forms,
    })
