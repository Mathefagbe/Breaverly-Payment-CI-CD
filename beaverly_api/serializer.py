from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import (KycDetails,KycDocumentImage,KycSelfie,KycUtilityBills,LivePhotoKyc)

class UserReadSerializer(serializers.ModelSerializer):
    class Meta:
        model=get_user_model()
        fields=[
            "first_name",
            "last_name",
            "email"
        ]

class EditProfileSerializer(serializers.ModelSerializer):
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
    image=serializers.ImageField(required=True)
    
class UploadKycFileSerializer(serializers.Serializer):
    file=serializers.FileField(required=True)
    
class KycDetailWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model=KycDetails
        exclude=[
            "user"
        ]

class KycDetailReadSerializer(serializers.ModelSerializer):
    user=UserReadSerializer(read_only=True)
    class Meta:
        model=KycDetails
        field="__all__"
         
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