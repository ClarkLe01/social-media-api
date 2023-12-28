# Generated by Django 4.1.6 on 2023-12-28 14:36

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0003_alter_user_first_name_alter_user_last_name"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="mute",
        ),
        migrations.AlterField(
            model_name="user",
            name="follow",
            field=models.ManyToManyField(
                blank=True, related_name="follow_user", to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
