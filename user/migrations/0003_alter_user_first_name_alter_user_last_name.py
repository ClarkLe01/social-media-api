# Generated by Django 4.1.6 on 2023-12-27 03:12

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0002_user_follow_user_mute"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="first_name",
            field=models.CharField(max_length=150, verbose_name="first name"),
        ),
        migrations.AlterField(
            model_name="user",
            name="last_name",
            field=models.CharField(max_length=150, verbose_name="last name"),
        ),
    ]
