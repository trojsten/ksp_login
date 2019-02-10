from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordChangeView,
)
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from social_django.models import UserSocialAuth
from social_django.views import disconnect as social_disconnect

from ksp_login.context_processors import login_providers
from ksp_login.forms import (KspUserCreationForm, PasswordChangeForm, UserProfileForm, get_profile_forms)
from ksp_login.utils import get_partial_pipeline


def login(request):
    return LoginView.as_view(
        redirect_authenticated_user=True,
        template_name='ksp_login/login.html',
        extra_context=login_providers(request))(request)


def logout(request):
    response = LogoutView.as_view(next_page='/')(request)
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
    return PasswordChangeView.as_view(
        success_url=reverse('account_settings'),
        form_class=form,
        template_name='ksp_login/password.html')(request)


def register(request, creation_form=KspUserCreationForm):
    """
    As the name suggests, registers a new user.

    Can replace the create_user function in the SOCIAL_AUTH pipeline
    (through ksp_login.pipeline.register_user) to make it possible for the
    user to pick a username.

    Also presents additional app-specific forms listed in the
    KSP_LOGIN_PROFILE_FORMS setting to the user.
    """
    if request.user.is_authenticated:
        return redirect('account_settings')
    partial = get_partial_pipeline(request)

    form_classes = [creation_form] + get_profile_forms()

    if request.method == "POST":
        forms = [form(request.POST, request=request)
                 for form in form_classes]
        if all(form.is_valid() for form in forms):
            user = forms[0].save()
            for form in forms[1:]:
                form.set_user(user)
                form.save()
            if not partial:
                return redirect('account_login')
            partial.kwargs['user'] = user.id
            partial.save()
            return redirect('social:complete', backend=partial.backend)
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

    return render(request, 'ksp_login/settings.html', dict(
        account_associations=UserSocialAuth.get_social_auth_for_user(
            request.user),
        forms=forms,
    ))
