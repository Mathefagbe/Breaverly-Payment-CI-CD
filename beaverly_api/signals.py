#when a user is created a signal otp is been sent out to the user

from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.template.loader import render_to_string
from .models import CapyMaxAccount,CapySafeAccount
from django.db import transaction

from .helper import generate_low_risk_id, generate_smartpro_id


# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def account_creation_handler(sender, instance, created, **kwargs):
#         try:
#             if created:
#                 CapyMaxAccount.objects.create(
#                     customer=instance,
#                     customer_code=generate_smartpro_id()
#                 )
#                 CapySafeAccount.objects.create(
#                     customer=instance,
#                     customer_code=generate_low_risk_id()
#                 )
#         except Exception as e:
#              raise RuntimeError("Error in sending email {}".format(e))
#              return None
        
