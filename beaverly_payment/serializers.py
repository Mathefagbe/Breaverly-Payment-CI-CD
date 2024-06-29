import io
import PyPDF2
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import (
                     TransactionHistory,ContractDuration,RepaymentSchedule
                     )
from drf_extra_fields.fields import Base64ImageField,Base64FileField

class Base64ImagesField(Base64ImageField):
    class Meta:
        swagger_schema_fields = {
            'type': 'String',
            'title': 'Image Content',
            'description': 'Content of the base64 encoded images',
            'read_only': False  # <-- FIX
        }

class PDFBase64FileField(Base64FileField):
    ALLOWED_TYPES = ['pdf']

    class Meta:
        swagger_schema_fields = {
            'type': 'string',
            'title': 'File Content',
            'description': 'Content of the file base64 encoded',
            'read_only': False  # <-- FIX
        }

    def get_file_extension(self, filename, decoded_file):
        try:
            PyPDF2.PdfFileReader(io.BytesIO(decoded_file))
        except PyPDF2.utils.PdfReadError as e:
            # logger.warning(e)
            raise serializers.ValidationError(e)
        else:
            return 'pdf'
        
class ContractDurationSerilaizer(serializers.ModelSerializer):
    class Meta:
        model=ContractDuration
        fields="__all__"

class RepaymentScheduleSerilaizer(serializers.ModelSerializer):
    class Meta:
        model=RepaymentSchedule
        fields="__all__"

class TransactionWriteSerializer(serializers.ModelSerializer):
    receipt=PDFBase64FileField(required=False)
    class Meta:
        model=TransactionHistory
        fields=[
            "receipt",
            "account_type",
            "amount",
            "currency",
            "payment_gateway",
            "contract_duration"
        ]
        extra_kwargs={
            "account_type":{
                "required":True
            },
            "amount":{
                "required":True
            },
            "contract_duration":{
                "required":True
            }
        }

#TopUp Deposit
class TopUpTransactionWriteSerializer(serializers.ModelSerializer):
    receipt=PDFBase64FileField(required=False)
    class Meta:
        model=TransactionHistory
        fields=[
            "receipt",
            "account_type",
            "amount",
            "currency",
            "payment_gateway",
            "transaction_fee"
        ]
        extra_kwargs={
            "account_type":{
                "required":True
            },
            "amount":{
                "required":True
            },
            "transaction_fee":{
                "default":0.97
            }
        }

    def validate(self, attrs):
        if attrs["payment_gateway"].lower() == "bank_transfer":
            raise RuntimeError("Please Upload Your Desposit Receipt")
        return super().validate(attrs)

#CapyBoost Deposit
class LeaverageTransactionWriteSerializer(serializers.ModelSerializer):
    receipt=PDFBase64FileField(required=False)
    class Meta:
        model=TransactionHistory
        fields=[
            "receipt",
            "account_type",
            "transaction_type",
            "amount",
            "currency",
            "payment_gateway",
            "repayment_schedule",
            "deposit_percentage",
            "inital_deposit", #initial_deposite + transaction fee
            "pay_off_amount",
        ]
        extra_kwargs={
            "account_type":{
                "required":False,
                "default":"CapySafe"
            },
            "transaction_type":{
                "required":False,
                "default":"capyboost"
            },
            "amount":{
                "required":True
            },
            "repayment_schedule":{
                "required":True
            },
            "deposit_percentage":{
                "required":True
            },
            "inital_deposit":{
                "required":True
            },
            "pay_off_amount":{
                "required":True
            }
        }

    def validate(self, attrs):
        if attrs["payment_gateway"].lower() == "bank_transfer":
            raise RuntimeError("Please Upload Your Desposit Receipt")
        return super().validate(attrs)
    
class UserReadTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model=get_user_model()
        fields=[
            "first_name",
            "last_name",
            "email",
            "middle_name",
            "phone_number",
            "image",
            "account_name",
            "bank_name",
            "account_number",
        ]

class TransactionReadSerializer(serializers.ModelSerializer):
    initiated_by=UserReadTransactionSerializer()
    received_by=UserReadTransactionSerializer()
    class Meta:
        model=TransactionHistory
        fields="__all__"
        depth=1
   

class AllDepositTransactionwriteSerializer(serializers.ModelSerializer):
    receipt=PDFBase64FileField(required=False)
    class Meta:
        model=TransactionHistory
        exclude=[
            "initiated_by"
        ]

class ChangeTransactionStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model=TransactionHistory
        fields=[
            "status"
        ]

class AmountSerializer(serializers.Serializer):
    amount=serializers.DecimalField(max_digits=10,decimal_places=2,required=True)


class TransferToBeaverlyMemberSerializer(serializers.Serializer):
    amount=serializers.DecimalField(max_digits=10,decimal_places=2,required=True)
    full_name=serializers.CharField()
    recipient_email=serializers.EmailField(required=True)

class WithdrawalSerializer(serializers.Serializer):
    bank_name=serializers.CharField(required=True)
    account_name=serializers.CharField(required=True)
    account_number=serializers.CharField(required=True)
    amount=serializers.DecimalField(max_digits=10,decimal_places=2,required=True)