# Generated by Django 5.1.4 on 2025-02-03 06:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_profile_converation'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='converation',
            new_name='conversation',
        ),
    ]
