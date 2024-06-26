import secrets
import string
from .models import TransactionHistory
from datetime import datetime,timezone,date
from dateutil.relativedelta import relativedelta


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
            trans_id="TRN_{}".format(invoice_id.lower())
            TransactionHistory.objects.get(transaction_id=trans_id)

        except TransactionHistory.DoesNotExist:
            return trans_id
        
def now() -> date:
    """Returns timezone aware datetime as at when run"""
    return datetime.utcnow().replace(tzinfo=timezone.utc).date()

def expire_date(duration):
    return now() + relativedelta(months=duration)