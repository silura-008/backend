from rest_framework import serializers
from .models import Profile,Preference,MoodLog,Task,Ratio

from djoser.serializers import UserCreateSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class UserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ("id", "email", "password")

class ProfileSerializer(serializers.ModelSerializer):
    class Meta :
        model = Profile
        fields = ("id", "user", "name","conversation")

class PreferenceSerializer(serializers.ModelSerializer):
    class Meta :
        model = Preference
        fields = '__all__'

class MoodLogSerializer(serializers.ModelSerializer):
    class Meta :
        model = MoodLog
        fields = '__all__'

class TaskSerializer(serializers.ModelSerializer):
    class Meta :
        model = Task
        fields = '__all__'

class RatioSerializer(serializers.ModelSerializer):
    class Meta :
        model = Ratio
        fields = '__all__'






