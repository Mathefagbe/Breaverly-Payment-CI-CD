#when a user is created a signal otp is been sent out to the user

from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.template.loader import render_to_string
from .models import Otp


@receiver(post_save, sender=Otp ,dispatch_uid="unique_identifier")
def send_otp_to_email(sender, instance, created, **kwargs):
        try:
            subject = 'Confirm Your Email Address'
            message = render_to_string('account/email_confirmation.html', {
            "otp":instance.otp
             })
            from_email = settings.EMAIL_HOST_USER
            to_email = instance.email
            send_mail(subject, message, from_email, [to_email], fail_silently=False)
            #save the email and the otp to email verification table
        except Exception as e:
             raise RuntimeError("Error in sending email {}".format(e))
             return None