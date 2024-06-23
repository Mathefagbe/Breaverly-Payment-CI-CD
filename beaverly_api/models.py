from django.db import models
import re
from django.conf import settings
from account.constant import SPECIAL_CHARS_REGEX
from django.core.validators import RegexValidator
import uuid
phone_validator = RegexValidator(
    r"^(\+?\d{0,4})?\s?-?\s?(\(?\d{3}\)?)\s?-?\s?(\(?\d{3}\)?)\s?-?\s?(\(?\d{4}\)?)?$",
    "The phone number provided is invalid",
)

class Permissions(models.Model):
    name=models.CharField(null=False)

class Role(models.Model):
    pass
# Create your models here.
class KycDocumentImage(models.Model):
    def upload_to(instance, filename):
        url = re.sub(
            SPECIAL_CHARS_REGEX,
            "_",
            "kyc/images/{filename}".format(filename=instance.user.first_name),
        )
        return url
    id=models.UUIDField(default=uuid.uuid4,db_index=True,primary_key=True)
    user=models.OneToOneField(settings.AUTH_USER_MODEL,unique=True,on_delete=models.CASCADE,related_name="user_kyc_image")
    has_verified=models.BooleanField(default=False)
    image=models.ImageField(upload_to=upload_to,null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

class KycSelfie(models.Model):
    def upload_to(instance, filename):
        url = re.sub(
            SPECIAL_CHARS_REGEX,
            "_",
            "kyc/selfie/{filename}".format(filename=instance.user.first_name),
        )
        return url
    id=models.UUIDField(default=uuid.uuid4,db_index=True,primary_key=True)
    user=models.OneToOneField(settings.AUTH_USER_MODEL,unique=True,on_delete=models.CASCADE,related_name="user_kyc_selfie")
    has_verified=models.BooleanField(default=False)
    image=models.ImageField(upload_to=upload_to,null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

class LivePhotoKyc(models.Model):
    def upload_to(instance, filename):
        url = re.sub(
            SPECIAL_CHARS_REGEX,
            "_",
            "kyc/live/{filename}".format(filename=instance.user.first_name),
        )
        return url
    id=models.UUIDField(default=uuid.uuid4,db_index=True,primary_key=True)
    user=models.OneToOneField(settings.AUTH_USER_MODEL,unique=True,on_delete=models.CASCADE,related_name="user_live_kyc")
    has_verified=models.BooleanField(default=False)
    image=models.ImageField(upload_to=upload_to,null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    
class KycUtilityBills(models.Model):
    def upload_to(instance, filename):
        url = re.sub(
            SPECIAL_CHARS_REGEX,
            "_",
            "kyc/files/{filename}".format(filename=instance.user.first_name),
        )
        return url
    id=models.UUIDField(default=uuid.uuid4,db_index=True,primary_key=True)
    user=models.OneToOneField(settings.AUTH_USER_MODEL,unique=True,on_delete=models.CASCADE,related_name="user_kyc_utility_bills")
    has_verified=models.BooleanField(default=False)
    file=models.FileField(upload_to=upload_to,null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

class KycDetails(models.Model):
    id=models.UUIDField(default=uuid.uuid4,db_index=True,primary_key=True)
    user=models.OneToOneField(settings.AUTH_USER_MODEL,unique=True,on_delete=models.CASCADE,related_name="user_kyc_details_bills")
    date_of_birth=models.DateField(null=True)
    phone_number=models.CharField(null=True,max_length=20,validators=[phone_validator])
    address=models.TextField()
    Nationality=models.CharField(max_length=100,null=True)
    industry=models.CharField(max_length=200,null=True)
    occupation=models.CharField(max_length=200,null=True)
    employer_name=models.CharField(max_length=200,null=True)
    employer_address=models.TextField()
    business_name=models.CharField(max_length=200,null=True)
    business_address=models.TextField()
    employment_status=models.CharField(max_length=200,null=True)
    source_of_fund=models.CharField(max_length=200,null=True)
    # has_verified=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)


