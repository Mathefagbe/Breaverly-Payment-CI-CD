from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.template.loader import render_to_string
from beaverly_api.models import CapyMaxAccount,CapySafeAccount
from django.db import transaction
from itertools import chain
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser,FormParser,MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from beaverly_api.helper import generate_low_risk_id, generate_smartpro_id


class CreateCapyMaxAccountApiView(APIView):
    def post(self,request):
        try:
            #check if user has created before
            if CapyMaxAccount.objects.filter(customer=request.user).exists():
                raise RuntimeError("You have already created CapyMax Account")
            
            CapyMaxAccount.objects.create(
                    customer=request.user,
                    customer_code=generate_smartpro_id()
                )
            res={
                "status":"success",
                "data":None,
                "message":"CapyMax Account Created Successfully"
            }
            return Response(res,status=status.HTTP_200_OK)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST) 
        
class CreateCapySafeAccountApiView(APIView):
    def post(self,request):
        try:
            #check if user has created before
            if CapySafeAccount.objects.filter(customer=request.user).exists():
                raise RuntimeError("You have already created CapySafe Account")
            
            CapySafeAccount.objects.create(
                    customer=request.user,
                    customer_code=generate_low_risk_id()
                )
            res={
                "status":"success",
                "data":None,
                "message":"CapySafe Account Created Successfully"
            }
            return Response(res,status=status.HTTP_200_OK)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST) 

        