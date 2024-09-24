from django.contrib.auth.models import AbstractUser
from django.db import models
from django_countries.fields import CountryField
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid

class CustomUser(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    post_code = models.CharField(max_length=20, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    country = CountryField(blank_label='(select country)', countries=['EU'])
    last_login = models.DateTimeField(auto_now=True)
    is_mfa_enabled = models.BooleanField(default=False)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

class PasswordResetToken(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.expires_at = timezone.now() + timezone.timedelta(hours=1)
        return super().save(*args, **kwargs)

    def is_valid(self):
        return timezone.now() < self.expires_at