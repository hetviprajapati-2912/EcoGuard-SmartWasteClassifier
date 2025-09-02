from django.contrib import admin
from .models import UserProfile, OTP, Activity

admin.site.register(UserProfile)
admin.site.register(OTP)
admin.site.register(Activity)
