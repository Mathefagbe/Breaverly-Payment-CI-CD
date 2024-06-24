from django.db import models
import re
from django.conf import settings
from account.constant import SPECIAL_CHARS_REGEX
from django.core.validators import RegexValidator,MaxValueValidator,MinValueValidator
import uuid
from .constant import( 
    ACCOUNT_STATUSES,CURRENCY,WITHDRAWAL_STATUS,
    TRANSACTION_TYPE,ACCOUNT_TYPE,GATEWAY)

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
    user=models.OneToOneField(settings.AUTH_USER_MODEL,unique=True,on_delete=models.CASCADE,related_name="user_kyc_selfie",db_index=True)
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
    user=models.OneToOneField(settings.AUTH_USER_MODEL,unique=True,on_delete=models.CASCADE,related_name="user_live_kyc",db_index=True)
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
    user=models.OneToOneField(settings.AUTH_USER_MODEL,unique=True,on_delete=models.CASCADE,related_name="user_kyc_utility_bills",db_index=True)
    has_verified=models.BooleanField(default=False)
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
    # has_verified=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

#Accounts
class CapySafeAccount(models.Model):
    id=models.UUIDField(default=uuid.uuid4,primary_key=True,db_index=True)
    customer_code=models.CharField(max_length=100,null=False,unique=True,db_index=True)
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="lowrisk_users",db_index=True)
    balance=models.DecimalField(max_digits=100,decimal_places=2,default=0.00)
    account_status = models.CharField(max_length=10, choices=ACCOUNT_STATUSES,default="ACTIVE")
    currency=models.CharField(max_length=10,default="NG",choices=CURRENCY)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    

    @property
    def kyc_status(self):
        pass

    @property
    def networth_balance(self):
        pass

class CapyMaxAccount(models.Model):
    id=models.UUIDField(default=uuid.uuid4,primary_key=True,db_index=True)
    customer_code=models.CharField(max_length=100,null=True,unique=True,db_index=True)
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="smartpro_users",db_index=True)
    balance=models.DecimalField(max_digits=100,decimal_places=2,default=0.00)
    account_status = models.CharField(max_length=10, choices=ACCOUNT_STATUSES,default="ACTIVE")
    currency=models.CharField(max_length=10,default="NG",choices=CURRENCY)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)


    @property
    def kyc_status(self):
        pass

    @property
    def networth_balance(self):
        pass
#widthdrawals
#when withdrawal is settle admin will delete that pending withdrawal
#when a user has money in pending he can withdrawal money from is balance
class PendingWithdrawals(models.Model):
    id=models.UUIDField(default=uuid.uuid4,primary_key=True,db_index=True)
    customer_code=models.CharField(max_length=100,null=True,unique=False,db_index=True)
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="pending_widthdrawal",db_index=True)
    balance=models.DecimalField(max_digits=100,decimal_places=2,default=0.00)
    currency=models.CharField(max_length=10,default="NG",choices=CURRENCY)
    status=models.CharField(max_length=20,default="pending",choices=WITHDRAWAL_STATUS)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)


#to put money in withdrawal balance u have to sell portfolio
#this will be automated from my code with 0.98% fee
class Withdrawals(models.Model):
    id=models.UUIDField(default=uuid.uuid4,primary_key=True,db_index=True)
    customer_code=models.CharField(max_length=100,null=True,unique=False,db_index=True)
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="widthdrawal",db_index=True)
    balance=models.DecimalField(max_digits=100,decimal_places=2,default=0.00)
    currency=models.CharField(max_length=10,default="NG",choices=CURRENCY)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)


#transaction History
class TransactionHistory(models.Model):
    def upload_to(instance, filename):
        url = re.sub(
            SPECIAL_CHARS_REGEX,
            "_",
            "transaction/receipt/{filename}".format(filename=instance.user.first_name),
        )
        return url
    id=models.UUIDField(default=uuid.uuid4,db_index=True,primary_key=True)
    transaction_id=models.CharField(db_index=True,null=True,max_length=20)
    receipt=models.FileField(upload_to=upload_to,null=True,blank=True)
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="user_transactions",db_index=True)
    account_type=models.CharField(default="CapySafe",max_length=30,choices=ACCOUNT_TYPE)
    transaction_type=models.CharField(default="deposit",max_length=30,choices=TRANSACTION_TYPE)
    status=models.CharField(max_length=20,default="pending",choices=WITHDRAWAL_STATUS)
    amount=models.DecimalField(max_digits=20,decimal_places=2,default=0.00)
    currency=models.CharField(choices=CURRENCY,default="NG",max_length=20)
    payment_gateway=models.CharField(choices=GATEWAY,max_length=20,null=True)
    deposit_percentage=models.FloatField(default=0.1,validators=[MinValueValidator(0.1),MaxValueValidator(1.0)])
    inital_deposit=models.DecimalField(max_digits=20,decimal_places=2,default=0.00)
    pay_off_amount=models.DecimalField(max_digits=20,decimal_places=2,default=0.00)
    leaverage_duration=models.IntegerField(null=True)
    transaction_fee=models.FloatField(null=True,validators=[MinValueValidator(0),MaxValueValidator(100.0)])
    expire_date=models.DateField(null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)


    @property
    def holding_schedule(self):
        if self.leaverage_duration:
            return "{} months - {}% Transaction Fee".format(self.leaverage_duration,self.transaction_fee)
        return None


# class EarningHistory(models.Model):
#     pass