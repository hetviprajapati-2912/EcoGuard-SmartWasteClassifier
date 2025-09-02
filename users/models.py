from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random
import string
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail

# Extra profile info if needed
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    def __str__(self):
        return self.user.username


# OTP model for 2FA
class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        # OTP expires in 5 minutes
        return not self.is_used and (timezone.now() - self.created_at).seconds < 300

    def __str__(self):
        return f"{self.user.username} - {self.code}"


# Activity model for CRUD
class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.title} ({self.user.username})"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        
