from django.dispatch import receiver

from ksp_login.forms import BaseUserProfileForm
from ksp_login.signals import user_form_requested
from ksp_login_tests.models import UserProfile


class UserProfileForm(BaseUserProfileForm):
    class Meta:
        model = UserProfile
        exclude = ['user']

@receiver(user_form_requested, dispatch_uid='user profile form')
def register_user_profile_form(sender, **kwargs):
    return UserProfileForm
