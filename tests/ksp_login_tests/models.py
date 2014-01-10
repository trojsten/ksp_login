from django.db import models


class UserProfile(models.Model):
    user = models.ForeignKey('auth.User')
    birthday = models.DateField(blank=True, null=True)
    shoe_size = models.PositiveSmallIntegerField(blank=True, null=True)
