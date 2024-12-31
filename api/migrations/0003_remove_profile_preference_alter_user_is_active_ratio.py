# Generated by Django 5.1.4 on 2024-12-24 17:07

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_moodlog_preference_profile_task'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='preference',
        ),
        migrations.AlterField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='Ratio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('happy_ratio', models.IntegerField(default=0)),
                ('sad_ratio', models.IntegerField(default=0)),
                ('angry_ratio', models.IntegerField(default=0)),
                ('anxious_ratio', models.IntegerField(default=0)),
                ('log_count', models.IntegerField(default=0)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='ratio', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]