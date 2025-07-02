from django.shortcuts import render
from rest_framework.views import APIView
# Create your views here.
from drf_yasg.utils import swagger_auto_schema
from .serializer import (UserRegistrationWriteSerializer,EmailVerificationSerializer,TokenObtainSerializer,
                         VerifiyOtpSerializer,PasswordResetSerializer,PinsWriteSerializer,ChangePinsWriteSerializer)
from rest_framework.response import Response
from rest_framework import status
from .helper import get_user_token
from rest_framework_simplejwt.views import (TokenObtainPairView)
from .models import Otp
from django.utils import timezone
from django.contrib.auth import get_user_model
import string
from django.utils.crypto import get_random_string
from rest_framework.parsers import JSONParser,FormParser,MultiPartParser
from beaverly_api.models import Roles
from django.db import transaction
from .models import Pins
from notifications.emails import send_emails

class UserRegistrationView(APIView):
    authentication_classes=[]
    permission_classes=[]

    @swagger_auto_schema(
            request_body=UserRegistrationWriteSerializer
    )
    def post(self, request):
        try:
            with transaction.atomic():
                serializer=UserRegistrationWriteSerializer(data=request.data)
                if serializer.is_valid(raise_exception=True):
                    data=serializer.save()
                    data.role.add(Roles.objects.get(role="customer"))
                    #Generate token after successfull registration

                res={
                    "status":"success",
                    "data":get_user_token(data),
                    "message":"Account Created Successfully"
                    }
                return Response(res,status=status.HTTP_201_CREATED)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)

class AdminUserRegistrationView(APIView):
    authentication_classes=[]
    permission_classes=[]

    @swagger_auto_schema(
            request_body=UserRegistrationWriteSerializer
    )
    @transaction.atomic()
    def post(self, request):
        try:
            serializer=UserRegistrationWriteSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                data=serializer.save()
                data.role.add(Roles.objects.get(role="admin"))
                #Generate token after successfull registration
            res={
                "status":"success",
                "data":get_user_token(data),
                "message":"Account Created Successfully"
                }
            return Response(res,status=status.HTTP_201_CREATED)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
        
class LoginApiView(TokenObtainPairView):

    @swagger_auto_schema(
            request_body=TokenObtainSerializer
    )
    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data=serializer.validated_data
            data.pop("refresh")
            res={
                "status":"success",
                "data":data,
                "message":"Login successfull"
            }
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
        
class PasswordResetApiView(APIView):
    authentication_classes=[]
    permission_classes=[]
    @swagger_auto_schema(
            request_body=PasswordResetSerializer
    )
    def post(self,request):
        try:
            res={}
            serializer=PasswordResetSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            email=serializer.validated_data['email']
            password=serializer.validated_data["password"]
            user=get_user_model().objects.get(email=email)
            user.set_password(password)
            user.confirm_password=user.set_password(password)
            user.save()
            res["status"]="success"
            res["data"]=get_user_token(user)
            res["message"]="Password Reset Successfully"
            return Response(res,status=status.HTTP_200_OK)  
        except get_user_model().DoesNotExist:
            res={
                "status":"Failed",
                "data":None,
                "message":"Invalid Otp"
            }
            return Response(res,status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)

class EmailVerificationApiView(APIView):
    authentication_classes=[]
    permission_classes=[]

    @swagger_auto_schema(
            request_body=EmailVerificationSerializer
    )
    def post(self,request):
        try:
            serializer=EmailVerificationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            email=serializer.validated_data["email"]

            otp=get_random_string(4,allowed_chars=string.digits)

            Otp.objects.filter(email=email).delete()
            obj=Otp.objects.create(email=email,otp=otp)
            #send an otp to that user
            send_emails(
                subject='Confirm Your Email Address',
                email=obj.email,
                template_name='account/email_confirmation.html',
                context={
                    "otp":obj.otp
                }
            )
            res={
                "status":"success",
                "data":None,
                "message":"Email verification sent to {}".format(email)
            }
            return Response(res,status=status.HTTP_200_OK)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
        
class VerifyOtpCodeAPiView(APIView):
    authentication_classes=[]
    permission_classes=[]
    
    @swagger_auto_schema(
            request_body= VerifiyOtpSerializer
    )
    def post(self,request):
        try:
            serializer=VerifiyOtpSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            #get the email and otp
            email=serializer.validated_data["email"]
            otp=serializer.validated_data["otp"]
            data=Otp.objects.get(email=email,otp=otp)
            #Check if code has not expired
            res={}
            if data.expire_at >= timezone.now():
                raise RuntimeError("Otp code has expired please resend otp") 
            #-----------------
            res["status"]="success"
            res["data"]=None
            res["message"]="Email Verification Successfull"
            return Response(res,status=status.HTTP_200_OK)  
        except Otp.DoesNotExist:
            res={
                "status":"Failed",
                "data":None,
                "message":"Invalid Otp"
            }
            return Response(res,status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)

class InputPinSerializerApiView(APIView):

    @swagger_auto_schema(
        request_body=PinsWriteSerializer
    )
    def post(self,request):
        try:
            serializer=PinsWriteSerializer(data=request.data,context={"request":request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            res={
                "status":"success",
                "data":None,
                "message":"Login Pin Set Successfully"
            }
            return Response(res,status=status.HTTP_200_OK)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
        
class ChangePinSerializerApiView(APIView):

    @swagger_auto_schema(
        request_body=ChangePinsWriteSerializer
    )
    def post(self,request):
        try:
            instance=Pins.objects.filter(email=request.user.email).first()
            if not instance:
                raise RuntimeError("You have not setup a login pin yet")
            serializer=ChangePinsWriteSerializer(instance=instance,data=request.data,context={"request":request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            res={
                "status":"success",
                "data":None,
                "message":"Login Pin Updated Successfully"
            }
            return Response(res,status=status.HTTP_200_OK)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
        
#transactionPin
class TransactionOtpPinApiView(APIView):
    def post(self,request):
        try:
            user=request.user
            email=user.email
            otp=get_random_string(4,allowed_chars=string.digits)
            Otp.objects.filter(email=email).delete()
            obj=Otp.objects.create(email=email,otp=otp)
            send_emails(
                subject='Confirm Your Email Address',
                email=obj.email,
                template_name='account/email_confirmation.html',
                context={
                    "full_name":user.full_name,
                    "pin":obj.otp,
                }
            )
            res={
                "status":"success",
                "data":None,
                "message":"Pin Sent To {}".format(email)
            }
            return Response(res,status=status.HTTP_200_OK)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)

class VerifyTransactionPinApiView(APIView):
    def get(self,request,pin):
        try:
            email=request.user.email
            data=Otp.objects.get(email=email,otp=pin)
            #Check if code has not expired
            res={}
            if data.expire_at >= timezone.now():
                raise RuntimeError("Pin has expired please resend otp") 
            #-----------------
            res["status"]="success"
            res["data"]=None
            res["message"]="Pin Verification Successfull"
            return Response(res,status=status.HTTP_200_OK)  
        except Otp.DoesNotExist:
            res={
                "status":"Failed",
                "data":None,
                "message":"Invalid Pin"
            }
            return Response(res,status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
        
class HideBalanceApiView(APIView):
    def put(self,request):
        try:
            user=request.user
            if user.hideBalance:
                user.hideBalance=False
                user.save()
            else:
                user.hideBalance=True
                user.save()
            res={
                "status":"Success",
                "data":None,
                "message":""
            }
            return Response(res,status=status.HTTP_200_OK)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)