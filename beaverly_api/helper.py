import secrets
import string
from .models import CapySafeAccount,CapyMaxAccount
from datetime import datetime,timezone,date
from dateutil.relativedelta import relativedelta
from .models import KycDocumentImage,KycSelfie,KycUtilityBills,LivePhotoKyc
from rest_framework.response import Response
from rest_framework import status
def generate_low_risk_id(length=15):
    while True:
        try:
            customer_code = "".join(
                secrets.choice(
                    string.ascii_uppercase + string.digits + string.ascii_lowercase
                )
                for i in range(length)
            )
            code="CUS_{}".format(customer_code.lower())
            CapySafeAccount.objects.get(customer_code=code)

        except CapySafeAccount.DoesNotExist:
            return code
        
def generate_smartpro_id(length=15):
    while True:
        try:
            customer_code = "".join(
                secrets.choice(
                    string.ascii_uppercase + string.digits + string.ascii_lowercase
                )
                for i in range(length)
            )
            code="CUS_{}".format(customer_code.lower())
            CapyMaxAccount.objects.get(customer_code=code)

        except CapyMaxAccount.DoesNotExist:
            return code
                

def check_kyc_validations(user):
    try:
        KycDocumentImage.objects.get(user=user)
       
        KycSelfie.objects.get(user=user)

        LivePhotoKyc.objects.get(user=user)

        KycUtilityBills.objects.get(user=user)

    except (KycSelfie.DoesNotExist,KycDocumentImage.DoesNotExist,KycUtilityBills.DoesNotExist,LivePhotoKyc.DoesNotExist) as e:
            raise RuntimeError("PLEASE COMPLETE YOUR KYC BEFORE CREATING AN ACCOUNT")
 