from django.db import models


class UserProfile(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    birthday = models.DateField(blank=True, null=True)
    shoe_size = models.SmallIntegerField(blank=True, null=True)
