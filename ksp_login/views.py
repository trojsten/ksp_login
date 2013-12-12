from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (login as auth_login, logout as
    auth_logout, password_change)
from django.contrib.auth.forms import SetPasswordForm
from social.apps.django_app.default.models import UserSocialAuth
from social.apps.django_app.utils import setting
from social.apps.django_app.views import disconnect as social_disconnect
from ksp_login import SOCIAL_AUTH_PARTIAL_PIPELINE_KEY
from ksp_login.context_processors import login_providers
from ksp_login.forms import (KspUserCreationForm, PasswordChangeForm,
    UserProfileForm)
from ksp_login.signals import user_form_requested


def login(request):
    if request.user.is_authenticated():
        next_page = request.REQUEST.get('next', 'account_settings')
        return redirect(next_page)
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

    Uses the user_form_requested signal to gather additional forms from
    other applications to present to the user.
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

    form_classes = [creation_form] + \
                   [form for receiver, form in
                    user_form_requested.send(sender=request, new_user=True)]

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

    Uses the user_form_requested signal to gather additional forms from
    other applications to present to the user.
    """
    form_classes = [settings_form] + \
                   [form for receiver, form in
                    user_form_requested.send(sender=request, new_user=False)]

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
