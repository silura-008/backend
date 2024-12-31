from django.contrib import admin
from .models import User, Profile, Preference, MoodLog, Task, Ratio

# Register your models here.

admin.site.register(User)
admin.site.register(Preference)
admin.site.register(Profile)
admin.site.register(MoodLog)
admin.site.register(Task)
admin.site.register(Ratio)