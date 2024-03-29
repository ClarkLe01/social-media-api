# Generated by Django 4.1.6 on 2023-05-31 17:09

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models

import chat.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="File",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("instance", chat.models.FileInstanceField(max_length=255)),
                ("type", models.CharField(max_length=255)),
                ("created", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ("created",),
            },
        ),
        migrations.CreateModel(
            name="Membership",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date_joined", models.DateField(auto_now_add=True)),
                ("role", models.CharField(blank=True, max_length=64, null=True)),
                ("nickname", models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Message",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("content", models.TextField(blank=True, null=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("isRemoved", models.BooleanField(default=False)),
                ("files", models.ManyToManyField(blank=True, null=True, to="chat.file")),
            ],
            options={
                "ordering": ("created",),
            },
        ),
        migrations.CreateModel(
            name="Seen",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                (
                    "member",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="seen_member",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "message",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="seen_message",
                        to="chat.message",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="RoomChat",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("roomName", models.CharField(blank=True, max_length=255, null=True)),
                ("isGroup", models.BooleanField(default=False)),
                ("updated", models.DateTimeField(default=django.utils.timezone.now)),
                ("roomAvatar", chat.models.AvatarRoomField(max_length=255)),
                (
                    "members",
                    models.ManyToManyField(
                        through="chat.Membership", to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="message",
            name="receiverID",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="message_receiver",
                to="chat.roomchat",
            ),
        ),
        migrations.AddField(
            model_name="message",
            name="senderID",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="message_sender",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="membership",
            name="room_chat",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="room_membership",
                to="chat.roomchat",
            ),
        ),
        migrations.AddField(
            model_name="membership",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="user_membership",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="file",
            name="room",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="file",
                to="chat.roomchat",
            ),
        ),
    ]
