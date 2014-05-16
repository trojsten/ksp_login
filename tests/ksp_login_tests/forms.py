from ksp_login.forms import BaseUserProfileForm
from ksp_login_tests.models import UserProfile


class UserProfileForm(BaseUserProfileForm):
    class Meta:
        model = UserProfile
        exclude = ['user']
