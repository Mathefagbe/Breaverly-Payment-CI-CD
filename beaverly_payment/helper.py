import secrets
import string
from .models import TransactionHistory
from datetime import datetime,timezone,date
from dateutil.relativedelta import relativedelta
from decimal import Decimal

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


def capyBoostTransaction(loan,deposit_amount,transaction_fee=0.98):
    net_deposit_amount=deposit_amount-Decimal(transaction_fee) #remove the transaction fee from the amount inputted
    if loan[0].payoff_amount == net_deposit_amount:
        loan_amount_repaid=loan[0].payoff_amount
        loan[0].payoff_amount -=net_deposit_amount
        loan[0].expire_date=None
        credited_amount=Decimal(0.00) # The balance is wat is been credited or sent out to the other user
        loan[0].save()
        return loan_amount_repaid,credited_amount
    if  loan[0].payoff_amount > net_deposit_amount:
        loan_amount_repaid=deposit_amount
        loan[0].payoff_amount -= net_deposit_amount #if the loan is more than the depost
        credited_amount=Decimal(0.00) # The balance is wat is been credited or sent out to the other user
        loan[0].save()
        return loan_amount_repaid,credited_amount
    if loan[0].payoff_amount < net_deposit_amount:
        loan_amount_repaid=loan[0].payoff_amount
        balance=net_deposit_amount - loan[0].payoff_amount # if the loan is less than the depost
        loan[0].payoff_amount=Decimal(0.00)
        loan[0].expire_date=None
        credited_amount=balance # The balance is wat is been credited or sent out to the other user
        loan[0].save()
        return loan_amount_repaid,credited_amount