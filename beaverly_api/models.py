from django.db import models
import re
from django.conf import settings
from account.constant import SPECIAL_CHARS_REGEX
from django.core.validators import RegexValidator,MaxValueValidator,MinValueValidator
import uuid
from .constant import( 
    ACCOUNT_STATUSES,CURRENCY,KYC_STATUS)

phone_validator = RegexValidator(
    r"^(\+?\d{0,4})?\s?-?\s?(\(?\d{3}\)?)\s?-?\s?(\(?\d{3}\)?)\s?-?\s?(\(?\d{4}\)?)?$",
    "The phone number provided is invalid",
)

class Permission(models.Model):
    permission = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Roles(models.Model):
    role = models.CharField(max_length=50, blank=True, null=True, unique=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class RolePermission(models.Model):
    role = models.ForeignKey(Roles, on_delete=models.CASCADE, blank=False, null=False,db_index=True)
    permission = models.ForeignKey(
        Permission, on_delete=models.CASCADE, blank=False, null=False,db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    user=models.OneToOneField(settings.AUTH_USER_MODEL,unique=True,on_delete=models.CASCADE,related_name="user_kyc_image",db_index=True)
    status=models.CharField(KYC_STATUS,max_length=10,default="unverified")
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
    user=models.OneToOneField(settings.AUTH_USER_MODEL,unique=True,on_delete=models.CASCADE,related_name="user_kyc_selfie",db_index=True)
    status=models.CharField(KYC_STATUS,max_length=10,default="unverified")
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
    user=models.OneToOneField(settings.AUTH_USER_MODEL,unique=True,on_delete=models.CASCADE,related_name="user_live_kyc",db_index=True)
    status=models.CharField(KYC_STATUS,max_length=10,default="unverified")
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
    user=models.OneToOneField(settings.AUTH_USER_MODEL,unique=True,on_delete=models.CASCADE,related_name="user_kyc_utility_bills",db_index=True)
    status=models.CharField(KYC_STATUS,max_length=10,default="unverified")
    file=models.FileField(upload_to=upload_to,null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

class KycDetails(models.Model):
    id=models.UUIDField(default=uuid.uuid4,db_index=True,primary_key=True)
    user=models.OneToOneField(settings.AUTH_USER_MODEL,unique=True,on_delete=models.CASCADE,related_name="user_kyc_details_bills",db_index=True)
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
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

#balances
class CapyBoostBalance(models.Model):
    id=models.UUIDField(default=uuid.uuid4,primary_key=True,db_index=True)
    customer=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="capyboost_users",db_index=True,null=True)
    payoff_amount=models.DecimalField(max_digits=100,decimal_places=2,default=0.00)
    currency=models.CharField(max_length=10,default="NG",choices=CURRENCY)
    repayment_schedule=models.CharField(max_length=300,null=True) #
    transaction_fee=models.FloatField(null=True,validators=[MinValueValidator(0),MaxValueValidator(100.0)])
    deposit_percentage=models.FloatField(null=True,validators=[MinValueValidator(0.1),MaxValueValidator(1.0)])
    inital_deposit=models.DecimalField(max_digits=20,decimal_places=2,null=True)
    expire_date=models.DateField(null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

#Accounts
class CapySafeAccount(models.Model):
    id=models.UUIDField(default=uuid.uuid4,primary_key=True,db_index=True)
    customer_code=models.CharField(max_length=100,null=False,unique=True,db_index=True)
    customer=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="capysafe_users",db_index=True,null=True)
    balance=models.DecimalField(max_digits=100,decimal_places=2,default=0.00)
    account_status = models.CharField(max_length=10, choices=ACCOUNT_STATUSES,default="ACTIVE")
    currency=models.CharField(max_length=10,default="NG",choices=CURRENCY)
    pay_off_amount=models.DecimalField(max_digits=100,decimal_places=2,default=0.00)
    expire_date=models.DateField(null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    

    @property
    def kyc_status(self):
        pass

        
class CapyMaxAccount(models.Model):
    id=models.UUIDField(default=uuid.uuid4,primary_key=True,db_index=True)
    customer_code=models.CharField(max_length=100,null=True,unique=True,db_index=True)
    customer=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="capymax_users",db_index=True,null=True)
    balance=models.DecimalField(max_digits=100,decimal_places=2,default=0.00)
    account_status = models.CharField(max_length=10, choices=ACCOUNT_STATUSES,default="ACTIVE")
    currency=models.CharField(max_length=10,default="NG",choices=CURRENCY)
    expire_date=models.DateField(null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)


    @property
    def kyc_status(self):
        pass

class Bank(models.Model):
    name=models.CharField(max_length=200,null=False,blank=False,db_index=True)
    type=models.CharField(max_length=20,null=True)
    slug=models.SlugField(db_index=True,null=True)
    code=models.CharField(max_length=20,null=True)
    currency=models.CharField(max_length=10,null=True)
    country=models.CharField(max_length=100,null=True)
    active=models.BooleanField(default=False)

