from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.utils.crypto import get_random_string
import string
from django.template.loader import render_to_string
from .models import Otp
from django.core.mail import send_mail
from django.utils import timezone

def get_user_token(user):
    data={}
    refresh=RefreshToken.for_user(user)
    data["access_token"]=str(refresh.access_token)
    return data



def sendUserEmailVerification(email):
        try:
            otp=get_random_string(4,allowed_chars=string.digits)
            subject = 'Confirm Your Email Address'
            message = render_to_string('account/email_confirmation.html', {
            "otp":otp
             })
            from_email = settings.EMAIL_HOST_USER
            to_email = email
            send_mail(subject, message, from_email, [to_email], fail_silently=False)
            #save the email and the otp to email verification table
            Otp.objects.filter(email=email).delete()
            Otp.objects.create(email=email,otp=otp)
        except Exception as e:
             raise RuntimeError("Error in sending email {}".format(e))
             return None
        

# def generatedTime():
#      return timezone.now() + timezone.timedelta(minutes=2)