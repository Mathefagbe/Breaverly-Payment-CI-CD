import io
import PyPDF2
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import (KycDetails,KycDocumentImage,KycSelfie,
                     KycUtilityBills,LivePhotoKyc,
                     LowRiskAccount,TransactionHistory
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


class UserReadSerializer(serializers.ModelSerializer):
    class Meta:
        model=get_user_model()
        fields=[
            "first_name",
            "last_name",
            "email"
        ]

class EditProfileSerializer(serializers.ModelSerializer):
    image=Base64ImagesField()
    class Meta:
        model=get_user_model()
        fields=[
            "image",
            "first_name",
            "last_name",
            "email",
            "middle_name",
            "phone_number",
            "account_name",
            "bank_name",
            "account_number"
        ]

class PersonalDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model=get_user_model()
        fields=[
            "full_name",
            "email",
            "phone_number",
            "registation_date"
        ]

class WithdrawalDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model=get_user_model()
        fields=[
            "account_name",
            "bank_name",
            "account_name"
        ]


class ImageUploadSerializer(serializers.Serializer):
    image=Base64ImagesField(required=True,use_url=True)

    
class UploadKycFileSerializer(serializers.Serializer):
    file=serializers.FileField(required=True)
    
class KycDetailWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model=KycDetails
        exclude=[
            "user",
            "id"
        ]

class KycDetailReadSerializer(serializers.ModelSerializer):
    user=UserReadSerializer(read_only=True)
    class Meta:
        model=KycDetails
        fields="__all__"
         
class KycImageReadSerializer(serializers.ModelSerializer):
    user=UserReadSerializer(read_only=True)
    class Meta:
        model=KycDocumentImage
        fields="__all__"

class KycUtilityBillsReadSerializer(serializers.ModelSerializer):
    user=UserReadSerializer()
    class Meta:
        model=KycUtilityBills
        fields="__all__"

class LivePhotoKycReadSerializer(serializers.ModelSerializer):
    user=UserReadSerializer()
    class Meta:
        model=LivePhotoKyc
        fields="__all__"

class KycSelfieReadSerializer(serializers.ModelSerializer):
    user=UserReadSerializer()
    class Meta:
        model=KycSelfie
        fields="__all__"

class TransactionWriteSerializer(serializers.ModelSerializer):
    receipt=PDFBase64FileField(required=False)
    class Meta:
        model=TransactionHistory
        fields=[
            "receipt",
            "account_type",
            "transaction_type",
            "amount",
            "currency",
            "payment_gateway"
        ]
        extra_kwargs={
            "account_type":{
                "required":True
            },
            "transaction_type":{
                "required":True
            },
            "amount":{
                "required":True
            },
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
    user=UserReadTransactionSerializer()
    class Meta:
        model=TransactionHistory
        fields="__all__"
        depth=1
   