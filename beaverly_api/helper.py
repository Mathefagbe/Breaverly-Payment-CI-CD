import secrets
import string
from .models import CapySafeAccount,CapyMaxAccount
from datetime import datetime,timezone,date
from dateutil.relativedelta import relativedelta

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
                
