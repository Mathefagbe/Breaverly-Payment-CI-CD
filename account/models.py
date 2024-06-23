import secrets
from django.apps import apps
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from account.constant import OTP_TYPE
from .constant import SPECIAL_CHARS_REGEX
import re
from datetime import datetime
import uuid



def generatedTime():
     return timezone.now() + timezone.timedelta(minutes=2)

phone_validator = RegexValidator(
    r"^(\+?\d{0,4})?\s?-?\s?(\(?\d{3}\)?)\s?-?\s?(\(?\d{3}\)?)\s?-?\s?(\(?\d{4}\)?)?$",
    "The phone number provided is invalid",
)
    

class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email or phone_number is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, phone_number, email, password, **extra_fields):
        """
        Create and save a User with the given email, phone_number and password.
        """
        if not email:
            raise ValueError(_("The Email must be set"))

        # if not phone_number:
        #     raise ValueError(_("The phone number must be set"))

        # if phone_number:
        #     num_object = phonenumbers.parse(phone_number, "NG")
        #     if not phonenumbers.is_valid_number(num_object):
        #         raise ValueError(_("The phone number is not valid"))

        email = self.normalize_email(email)
        user = self.model(email=email, phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, phone_number, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email phone_number and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(phone_number, email, password, **extra_fields)
    
class OTPManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(created_at__gte=timezone.now() - timezone.timedelta(minutes=5))
        )

class User(AbstractUser):
    def upload_to(instance, filename):
        url = re.sub(
            SPECIAL_CHARS_REGEX,
            "_",
            "images/feeds/{filename}".format(filename=instance.first_name),
        )
        return url
    username=None
    id=models.UUIDField(default=uuid.uuid4,db_index=True,primary_key=True)
    confirm_password=models.CharField(max_length=100,null=False,blank=False)
    email = models.EmailField(_('email address'), blank=True,unique=True,db_index=True)
    middle_name=models.CharField(max_length=100,null=True,blank=True)
    phone_number=models.CharField(max_length=13,null=True,blank=True)
    image=models.ImageField(upload_to=upload_to,null=True,blank=True)
    account_name=models.CharField(max_length=100,null=True,blank=True)
    bank_name=models.CharField(max_length=100,null=True,blank=True)
    has_verified_email=models.BooleanField(default=False)
    account_number=models.CharField(max_length=15,null=True,blank=True)
    created_at=models.DateField(auto_now=True)
    registation_date=models.DateField(auto_now=datetime.now().date)
    # role=models.ManyToManyField()
    objects=CustomUserManager()

    USERNAME_FIELD="email"
    REQUIRED_FIELDS=[]

    @property
    def full_name(self):
        return self.get_full_name()
    

    def has_verfied_kyc(self):
        pass

    def kyc_verification_steps(self):
        pass
        #check if the user has uploaded his detail
        #check if id,selfie,document,holdingIDcard

    def get_user_permissions(self):
        pass

class Otp(models.Model):
    otp=models.CharField(max_length=4,null=False,blank=False)
    email=models.CharField(max_length=200,null=True,blank=False,db_index=True)
    otp_type=models.CharField(choices=OTP_TYPE,max_length=20,null=False)
    created_at=models.DateTimeField(auto_now_add=True)
    expire_at=models.DateTimeField(default=generatedTime)

    # objects=OTPManager()

class Bank(models.Model):
    name=models.CharField(max_length=200,null=False,blank=False,db_index=True)
    type=models.CharField(max_length=20,null=True)
    slug=models.SlugField(db_index=True,null=True)
    code=models.CharField(max_length=20,null=True)
    currency=models.CharField(max_length=10,null=True)
    country=models.CharField(max_length=100,null=True)
    active=models.BooleanField(default=False)



