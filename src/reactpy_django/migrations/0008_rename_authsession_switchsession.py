# Generated by Django 5.1.4 on 2024-12-24 22:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reactpy_django', '0007_authsession'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='AuthSession',
            new_name='SwitchSession',
        ),
    ]
