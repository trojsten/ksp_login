from django.dispatch import Signal


# This signal is used to gather the list of forms to be displayed to the
# user as the user profile.
user_form_requested = Signal(providing_args=['new_user'])
