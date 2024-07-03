from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainSerializer,TokenObtainPairSerializer
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from .models import Pins
from django.contrib.auth.hashers import make_password, check_password

User=get_user_model()

class UserRegistrationWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model=get_user_model()
        fields=[
            "first_name",
            "last_name",
            "email",
            "password",
            "confirm_password"
        ]
    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise RuntimeError("Password does not match")
        return super().validate(attrs)

    def create(self, validated_data):
        user=User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.confirm_password=user.password
        user.save()
        return user

class UserRegistrationReadSerializer(serializers.ModelSerializer):
    class Meta:
        model=get_user_model()
        fields=[
            "first_name",
            "last_name",
            "email"
        ]

class EmailVerificationSerializer(serializers.Serializer):
    email=serializers.EmailField(required=True)

class TokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {
        "no_active_account": _("login provided credentials does not exist")
    }
    # token_class = RefreshToken
    
    def validate_email(self,data):
        if get_user_model().objects.filter(email__iexact=data).exists():
            return data
        raise serializers.ValidationError("Invaild email please check your email")

class VerifiyOtpSerializer(serializers.Serializer):
    otp=serializers.CharField(max_length=4,required=True)
    email=serializers.EmailField(required=True)

    def validate_email(self, data):
        if get_user_model().objects.filter(email=data).exists():
            return data
        raise serializers.ValidationError("Invalid Email")
    
class PasswordResetSerializer(serializers.Serializer):
    email=serializers.EmailField(required=True)
    password=serializers.CharField(required=True)
    confirm_password=serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs["password"] == attrs["confirm_password"]:
            return super().validate(attrs)
        raise RuntimeError("Password does not match, Pleas re-enter password")
    

class PinsWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model=Pins
        fields=[
            "pin"
        ]
    
    def create(self, validated_data):
        if self.Meta.model.objects.filter(email=self.context["request"].user.email).exists():
            raise RuntimeError("You have already setup your login pin")
        hash_pin= make_password(validated_data["pin"])
        pin=Pins.objects.create(
            pin=hash_pin,
            email=self.context["request"].user.email
        )
        return pin
    

class ChangePinsWriteSerializer(serializers.ModelSerializer):
    old_pin=serializers.CharField(required=True)
    class Meta:
        model=Pins
        fields=[
            "pin",
            "old_pin"
        ]
    
    def update(self, instance, validated_data):
        old_pin=validated_data["old_pin"]
        new_pin=validated_data["pin"]
        if not check_password(old_pin,encoded=instance.pin):
            raise RuntimeError("Incorrect Old Pin")
        instance.pin=make_password(new_pin)
        instance.save()
        return instance
    

