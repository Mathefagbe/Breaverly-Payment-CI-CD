from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainSerializer,TokenObtainPairSerializer
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

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
    

