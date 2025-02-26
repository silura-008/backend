from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.timezone import now
from django.conf import settings
from datetime import date, datetime,timezone


# User


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    date_created = models.DateTimeField(default=now)
    date_modified = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):

        if (self.is_active and not Ratio.objects.filter(user=self).exists()):
            Preference.objects.create(user=self)
            Profile.objects.create(user=self)
            Ratio.objects.create(user=self)
           
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email
    

# Preference

DEFAULT_PREFERENCES = {"video": True, "article": True, "story": True}

class Preference(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='preference'
    )
    on_happy = models.JSONField(default=DEFAULT_PREFERENCES)
    on_sad = models.JSONField(default=DEFAULT_PREFERENCES)
    on_angry = models.JSONField(default=DEFAULT_PREFERENCES)
    on_anxious = models.JSONField(default=DEFAULT_PREFERENCES)
    on_fear = models.JSONField(default=DEFAULT_PREFERENCES)

    def __str__(self):
        return f"Preferences of {self.user.email}"

# Profile

class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    name = models.CharField(max_length=50, blank=True,null = True)
    country = models.TextField(blank=True, null=True,default="Country")
    conversation = models.JSONField(default=list)
    # avatar = models.ImageField(
    #     upload_to='avatars/',
    #     default='avatars/default.png'
    # )
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)

    def append_to_conversation(self, sender, text):
        
        if not isinstance(self.conversation, list):
            self.conversation = []
        message = {
            "id": len(self.conversation) + 1,
            "sender": sender,
            "text": text,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "time": datetime.now().strftime("%I:%M %p"),
        }
        self.conversation.append(message)
        self.save()

    def save(self, *args, **kwargs):
        if not self.name and self.user.email:
            self.name = self.user.email.split('@')[0]

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Profile of {self.user.email}"

# MoodLog


def percentage(x,t):
    if (x==0 or t==0):
        return 0
    else :
        return (x/t)*100

class MoodLog(models.Model):
    MOOD_CHOICES = [
        ('sad', 'Sad'),
        ('angry', 'Angry'),
        ('anxious', 'Anxious'),
        ('happy', 'Happy'),
    ]
    
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    mood = models.CharField(max_length=50, choices=MOOD_CHOICES)
    note = models.TextField(blank=True, null=True)
    task_rate = models.IntegerField(default=0)

    def update_ratio(self):
        r = Ratio.objects.get(user=self.user)
        count = MoodLog.objects.filter(user=self.user).count() 
        r.log_count = count
        r.happy_ratio = percentage(MoodLog.objects.filter(user=self.user,mood ='happy').count(),count)
        r.sad_ratio = percentage(MoodLog.objects.filter(user=self.user,mood ='sad').count(),count)
        r.angry_ratio = percentage(MoodLog.objects.filter(user=self.user,mood ='angry').count(),count)
        r.anxious_ratio = percentage(MoodLog.objects.filter(user=self.user,mood ='anxious').count(),count)
        r.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_ratio()
        
    def __str__(self):
        return f"MoodLog for {self.user.email} on {self.date}"


# Task

class Task(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    tasks = models.JSONField(default=dict) 
    rate = models.IntegerField(default=0) 
    date = models.DateField(default=date.today) 

    def update_rate(self):
        total_tasks = len(self.tasks)
        completed_tasks = sum(1 for task in self.tasks.values() if task)
        self.rate = (completed_tasks / total_tasks) * 100

    def update_moodlog_rate(self):
        if( not self.date < date.today()):
            moodlog = MoodLog.objects.filter(user=self.user , date=date.today()).first()
            if(moodlog):
                moodlog.task_rate = self.rate
                moodlog.save()

    def save(self, *args, **kwargs):
            self.update_rate()
            self.update_moodlog_rate()
            super().save(*args, **kwargs)

    def __str__(self):
            return f"Tasks for {self.user.email} on {self.date}"

# Ratio


class Ratio(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ratio'
    )
    happy_ratio = models.IntegerField(default=0)
    sad_ratio = models.IntegerField(default=0)
    angry_ratio = models.IntegerField(default=0)
    anxious_ratio = models.IntegerField(default=0)
    log_count = models.IntegerField(default=0)

    def __str__(self):
            return f"Ratios for {self.user.email}"
