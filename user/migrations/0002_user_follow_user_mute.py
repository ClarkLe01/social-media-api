# Generated by Django 4.1.6 on 2023-06-06 03:26

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='follow',
            field=models.ManyToManyField(blank=True, null=True, related_name='follow_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='user',
            name='mute',
            field=models.ManyToManyField(blank=True, null=True, related_name='mute_notification', to=settings.AUTH_USER_MODEL),
        ),
    ]
