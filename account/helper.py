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