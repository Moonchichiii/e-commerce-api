from django.contrib.auth.models import AbstractUser
from django.db import models
from django_countries.fields import CountryField

class CustomUser(AbstractUser):
    address = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    country = CountryField(blank_label='(select country)', countries=['EU'])
    last_login = models.DateTimeField(auto_now=True)
    is_mfa_enabled = models.BooleanField(default=False)

    def __str__(self):
        return self.email
