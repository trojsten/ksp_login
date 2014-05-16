DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db',
    },
}

SECRET_KEY = '47'

DEBUG = True

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'social.apps.django_app.default',
    'ksp_login',
    'ksp_login_tests',
)

ROOT_URLCONF = 'ksp_login_tests.urls'

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
    "ksp_login.context_processors.login_providers_both",
)

STATIC_ROOT = ''
STATIC_URL = '/static/'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

LOGIN_URL = '/account/login/'
LOGIN_REDIRECT_URL = '/account/'

AUTHENTICATION_BACKENDS = (
    'social.backends.facebook.FacebookOAuth2',
    'social.backends.google.GoogleOpenId',
    'social.backends.github.GithubOAuth2',
    'ksp_login.backends.LaunchpadAuth',
    'social.backends.open_id.OpenIdAuth',
    'django.contrib.auth.backends.ModelBackend',
    'ksp_login_tests.social_backend.DummyTestingAuth1',
)

AUTHENTICATION_PROVIDERS_BRIEF = 3

SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'ksp_login.pipeline.register_user',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details',
)

KSP_LOGIN_PROFILE_FORMS = (
    'ksp_login_tests.forms.UserProfileForm',
)
