from django.db import models
import re
from django.conf import settings
from account.constant import SPECIAL_CHARS_REGEX
from django.core.validators import RegexValidator,MaxValueValidator,MinValueValidator
import uuid
from .constant import( 
    CURRENCY,WITHDRAWAL_STATUS,
    TRANSACTION_TYPE,ACCOUNT_TYPE,GATEWAY)

phone_validator = RegexValidator(
    r"^(\+?\d{0,4})?\s?-?\s?(\(?\d{3}\)?)\s?-?\s?(\(?\d{3}\)?)\s?-?\s?(\(?\d{4}\)?)?$",
    "The phone number provided is invalid",
)

#widthdrawals
#when withdrawal is settle admin will delete that pending withdrawal
#when a user has money in pending he can withdrawal money from is balance
class PendingWithdrawals(models.Model):
    id=models.UUIDField(default=uuid.uuid4,primary_key=True,db_index=True)
    customer_code=models.CharField(max_length=100,null=True,unique=False,db_index=True)
    customer=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="pending_widthdrawal",db_index=True)
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
    customer=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="widthdrawal",db_index=True)
    balance=models.DecimalField(max_digits=100,decimal_places=2,default=0.00)
    currency=models.CharField(max_length=10,default="NG",choices=CURRENCY)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

class ContractDuration(models.Model):
    title=models.TextField()
    contract_duration=models.IntegerField()

class RepaymentSchedule(models.Model):
    title=models.TextField()
    repayment_duration=models.IntegerField()
    transaction_fee=models.FloatField(null=True)

#transaction History/ledger
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
    initiated_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="user_transactions",db_index=True)
    received_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="reciever",db_index=True,null=True)
    account_type=models.CharField(max_length=30,choices=ACCOUNT_TYPE,null=True)
    transaction_type=models.CharField(default="deposit",max_length=30,choices=TRANSACTION_TYPE)
    status=models.CharField(max_length=20,default="pending",choices=WITHDRAWAL_STATUS)
    amount=models.DecimalField(max_digits=20,decimal_places=2,default=0.00) #amount deposited or transfered
    # amount_charged=models.DecimalField(max_digits=20,decimal_places=2,default=0.00) 
    amount_settled=models.DecimalField(max_digits=20,decimal_places=2,default=0.00) #amount deposited or transfered i.e netamount if loan is involved
    amount_repaid=models.DecimalField(max_digits=20,decimal_places=2,default=0.00)
    currency=models.CharField(choices=CURRENCY,default="NG",max_length=20)
    payment_gateway=models.CharField(choices=GATEWAY,max_length=20,null=True)
    deposit_percentage=models.FloatField(null=True,validators=[MinValueValidator(1),MaxValueValidator(100)])
    inital_deposit=models.DecimalField(max_digits=20,decimal_places=2,null=True)
    pay_off_amount=models.DecimalField(max_digits=20,decimal_places=2,null=True) #payoffamount due to loan
    contract_duration=models.CharField(max_length=300,null=True) #
    repayment_schedule=models.CharField(max_length=300,null=True) #
    bank_details=models.JSONField(null=True)
    transaction_fee=models.FloatField(null=True,validators=[MinValueValidator(0),MaxValueValidator(100.0)])
    expire_date=models.DateField(null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)


# class EarningHistory(models.Model):
#     pass