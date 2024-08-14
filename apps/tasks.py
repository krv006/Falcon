from celery import shared_task
from django.core.mail import send_mail

from root import settings


@shared_task
def send_to_email(msg: str, email: str):
    subject = 'Tema'
    send_mail(subject, msg, settings.EMAIL_HOST_USER, [email])
