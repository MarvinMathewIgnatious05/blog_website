from django.db import models
from django.contrib.auth.models import AbstractUser
import os

def user_profile_upload_path(instance, filename):
    """
    Path format: users/<user_id>/profile/profile.<ext>
    """
    ext = filename.split('.')[-1].lower()
    user_id = instance.id if instance.id else (instance.username or 'temp')
    return os.path.join('users', str(user_id), 'profile', f'profile.{ext}')

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to=user_profile_upload_path, blank=True, null=True)

    def __str__(self):
        return '{}'.format(self.username)

