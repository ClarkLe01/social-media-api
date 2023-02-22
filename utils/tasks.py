from celery.utils.log import get_task_logger
from django.core.mail import EmailMessage
from datetime import datetime
from celery import shared_task

logger = get_task_logger(__name__)


@shared_task
def send_email(mail_subject, messages, recipients):
    # email = EmailMessage(mail_subject, messages, to=recipients)
    # email.content_subtype = 'html'
    # email.send(fail_silently=True)
    print("send email to {0} at {1}".format(recipients, datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
    logger.info("send email to {0} at {1}".format(recipients, datetime.now().strftime("%d/%m/%Y %H:%M:%S")))


@shared_task
def sample_task():
    print("Sample task here")
    logger.info("Sample task here")
