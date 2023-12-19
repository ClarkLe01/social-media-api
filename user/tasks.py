import os

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage, get_connection


@shared_task
def send_email(mail_subject, messages, recipients):
    with get_connection(
        host=settings.EMAIL_HOST,
        port=settings.EMAIL_PORT,
        username=settings.EMAIL_HOST_USER,
        password=settings.EMAIL_HOST_PASSWORD,
        use_tls=settings.EMAIL_USE_TLS,
    ) as connection:
        email = EmailMessage(
            mail_subject,
            messages,
            from_email=settings.EMAIL_HOST_USER,
            to=recipients,
            connection=connection,
        )
        email.content_subtype = "html"
        email.send(fail_silently=True)
