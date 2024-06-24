from account.models import Bank
from .bank_list import bank_list

def load_banks():
    try:
        for bank in bank_list:
            bank.pop("longCode")
            bank.pop("gateway")
            Bank.objects.get_or_create(code=bank["code"], defaults=bank)
    except Exception as e:
            print(e)