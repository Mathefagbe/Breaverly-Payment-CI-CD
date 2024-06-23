import secrets
import string
from .models import LowRiskAccount,SmartProAccount,TransactionHistory
def generate_low_risk_id(length=15):
    while True:
        try:
            customer_code = "".join(
                secrets.choice(
                    string.ascii_uppercase + string.digits + string.ascii_lowercase
                )
                for i in range(length)
            )
            code="CUS_{}".format(customer_code)
            LowRiskAccount.objects.get(customer_code=code)

        except LowRiskAccount.DoesNotExist:
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
            code="CUS_{}".format(customer_code)
            SmartProAccount.objects.get(customer_code=code)

        except SmartProAccount.DoesNotExist:
            return code
        
def generate_invoice_id(length=8):
    """Generates invoice id"""
    while True:
        try:
            invoice_id = "".join(
                secrets.choice(
                    string.ascii_uppercase + string.digits + string.ascii_lowercase
                )
                for i in range(length)
            )
            trans_id="TRN_{}".format(invoice_id)
            TransactionHistory.objects.get(transaction_id=trans_id)

        except TransactionHistory.DoesNotExist:
            return trans_id