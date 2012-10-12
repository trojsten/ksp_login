from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _


class KspUserCreationForm(UserCreationForm):
    """
    A custom user creation form that can make the password fields
    optional.
    """
    class Meta(UserCreationForm.Meta):
        fields = ('username', 'first_name', 'last_name', 'email')

    def __init__(self, password_required=True, *args, **kwargs):
        super(KspUserCreationForm, self).__init__(*args, **kwargs)
        self.password_required = password_required

        if not password_required:
            self.fields['password1'].required = False
            self.fields['password2'].required = False
            self.fields['password1'].help_text = _(
                "Since you're logging in using an external provider, "
                "this field is optional; however, by supplying it, you "
                "will be able to log in using a password."
            )

    def clean_password2(self):
        """
        We need to validate the submitted passwords if they are required
        or either has been submitted, otherwise the user account will be
        passwordless.
        """
        if (self.password_required or self.cleaned_data.get('password1') or
            self.cleaned_data.get('password2')):
            return super(KspUserCreationForm, self).clean_password2()
        return None

    def save(self, commit=True):
        """
        If a password was provided or is required, just delegate to the
        parent's save, otherwise explicitly set an unusable password.
        """
        user = super(KspUserCreationForm, self).save(commit=False)
        if not (self.cleaned_data.get('password1') or
                self.password_required):
            user.set_unusable_password()
        if commit:
            user.save()
        return user
