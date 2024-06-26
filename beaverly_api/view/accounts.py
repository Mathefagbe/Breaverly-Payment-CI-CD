from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.template.loader import render_to_string
from beaverly_api.models import CapyMaxAccount,CapySafeAccount,CapyBoostBalance
from django.db import transaction
from itertools import chain
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser,FormParser,MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from beaverly_api.helper import generate_low_risk_id, generate_smartpro_id
from beaverly_api.serializer import (CapySafeAccountReadSerializer,CapyBoostBalanceReadSerializer,
    CapyMaxAccountReadSerializer,UpdateCustomeAccountBalanceSerializer,UpdateCustomeCapyBoostBalanceSerializer)
from drf_yasg.openapi import IN_QUERY, Parameter
from beaverly_api import permissions as app_permissions

INSUFFICIENT_PERMISSION="INSUFFICIENT_PERMISSION"
PERMISSION_MESSAGE="PERMISSION DENIED"

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
        
    def get(self,request):
        try:
            account=CapyMaxAccount.objects.get(customer=request.user)
            res={
                "status":"success",
                "data":CapyMaxAccountReadSerializer(account).data,
                "message":"CapyMax Account fetch Successfully"
            }
            return Response(res,status=status.HTTP_200_OK)  
        except CapySafeAccount.DoesNotExist as e:
            res={
                "status":"Failed",
                "data":None,
                "message":"Customer does not have capyMax account"
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
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
        
    
    def get(self,request):
        try:
            account=CapySafeAccount.objects.get(customer=request.user)
            res={
                "status":"success",
                "data":CapySafeAccountReadSerializer(account).data,
                "message":"CapySafe Account fetch Successfully"
            }
            return Response(res,status=status.HTTP_200_OK)  
        except CapySafeAccount.DoesNotExist as e:
            res={
                "status":"Failed",
                "data":None,
                "message":"Customer does not have capysafe account"
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
      
class CapyMaxCustomersAccountsApiview(APIView):
    @swagger_auto_schema(
            manual_parameters=[
                Parameter("search",IN_QUERY,type="str",required=False)
            ]
    )
    def get(self,request):
        try:
            if app_permissions.CAN_VIEW_CUSTOMER_ACCOUNT not in request.user.get_user_permissions():
                    res={
                        "status":"Failed",
                        "data":None,
                        "message":PERMISSION_MESSAGE
                    }
                    return Response(res,status=status.HTTP_403_FORBIDDEN)
            search=request.GET.get("search",None)
            account=CapyMaxAccount.objects.select_related("customer").order_by("-created_at").all()
            if search:
                account=account.filter(customer__email=search,customer_code=search)
            res={
                "status":"success",
                "data":CapyMaxAccountReadSerializer(account,many=True).data,
                "message":"CapyMax Account fetch Successfully"
            }
            return Response(res,status=status.HTTP_200_OK)  
        except CapyMaxAccount.DoesNotExist as e:
            res={
                "status":"Failed",
                "data":None,
                "message":"Customer does not have capyMax account"
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
        
class CapySafeCustomersAccountsApiview(APIView):
    @swagger_auto_schema(
            manual_parameters=[
                Parameter("search",IN_QUERY,type="str",required=False)
            ]
    )
    def get(self,request):
        try:
            if app_permissions.CAN_VIEW_CUSTOMER_ACCOUNT not in request.user.get_user_permissions():
                    res={
                        "status":"Failed",
                        "data":None,
                        "message":PERMISSION_MESSAGE
                    }
                    return Response(res,status=status.HTTP_403_FORBIDDEN)
            search=request.GET.get("search",None)
            account=CapySafeAccount.objects.select_related("customer").order_by("-created_at").all()
            if search:
                account=account.filter(customer__email=search,customer_code=search)
            res={
                "status":"success",
                "data":CapySafeAccountReadSerializer(account,many=True).data,
                "message":"CapySafe Account fetch Successfully"
            }
            return Response(res,status=status.HTTP_200_OK)  
        except CapySafeAccount.DoesNotExist as e:
            res={
                "status":"Failed",
                "data":None,
                "message":"Customer does not have capySafe account"
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
        
class UpdateCustomerCapysafeBalanceApiView(APIView):
    def get(self,request,id):
        try:
            if app_permissions.CAN_VIEW_CUSTOMER_ACCOUNT not in request.user.get_user_permissions():
                    res={
                        "status":"Failed",
                        "data":None,
                        "message":PERMISSION_MESSAGE
                    }
                    return Response(res,status=status.HTTP_403_FORBIDDEN)
            account=CapySafeAccount.objects.get(id=id)
            res={
                "status":"success",
                "data":CapySafeAccountReadSerializer(account).data,
                "message":"CapySafe Account fetch Successfully"
            }
            return Response(res,status=status.HTTP_200_OK)  
        except CapySafeAccount.DoesNotExist as e:
            res={
                "status":"Failed",
                "data":None,
                "message":"Customer does not have capysafe account"
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)   
        
    @swagger_auto_schema(
            request_body=UpdateCustomeAccountBalanceSerializer
    )
    def put(self,request,id):
        try:
            if app_permissions.CAN_VIEW_CUSTOMER_ACCOUNT not in request.user.get_user_permissions():
                    res={
                        "status":"Failed",
                        "data":None,
                        "message":PERMISSION_MESSAGE
                    }
                    return Response(res,status=status.HTTP_403_FORBIDDEN)
            account=CapySafeAccount.objects.get(id=id)
            serializer=UpdateCustomeAccountBalanceSerializer(instance=account,data=request.data)
            serializer.is_valid(raise_exception=True)
            account.balance=serializer.validated_data["balance"]
            account.save()
            res={
                "status":"success",
                "data":None,
                "message":"CapySafe Balance updated Successfully"
            }
            return Response(res,status=status.HTTP_200_OK)  
        except CapySafeAccount.DoesNotExist as e:
            res={
                "status":"Failed",
                "data":None,
                "message":"Customer does not have capysafe account"
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST) 
           
class UpdateCustomerCapyMaxBalanceApiView(APIView):
    def get(self,request,id):
        try:
            if app_permissions.CAN_VIEW_CUSTOMER_ACCOUNT not in request.user.get_user_permissions():
                    res={
                        "status":"Failed",
                        "data":None,
                        "message":PERMISSION_MESSAGE
                    }
                    return Response(res,status=status.HTTP_403_FORBIDDEN)
            account=CapyMaxAccount.objects.get(id=id)
            res={
                "status":"success",
                "data":CapyMaxAccountReadSerializer(account).data,
                "message":"CapyMax Account fetch Successfully"
            }
            return Response(res,status=status.HTTP_200_OK)  
        except CapyMaxAccount.DoesNotExist as e:
            res={
                "status":"Failed",
                "data":None,
                "message":"Customer does not have capyMax account"
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)   
        
    @swagger_auto_schema(
            request_body=UpdateCustomeAccountBalanceSerializer
    )
    def put(self,request,id):
        try:
            if app_permissions.CAN_VIEW_CUSTOMER_ACCOUNT not in request.user.get_user_permissions():
                    res={
                        "status":"Failed",
                        "data":None,
                        "message":PERMISSION_MESSAGE
                    }
                    return Response(res,status=status.HTTP_403_FORBIDDEN)
            account=CapyMaxAccount.objects.get(id=id)
            serializer=UpdateCustomeAccountBalanceSerializer(instance=account,data=request.data)
            serializer.is_valid(raise_exception=True)
            account.balance=serializer.validated_data["balance"]
            account.save()
            res={
                "status":"success",
                "data":None,
                "message":"CapyMax Balance updated Successfully"
            }
            return Response(res,status=status.HTTP_200_OK)  
        except CapySafeAccount.DoesNotExist as e:
            res={
                "status":"Failed",
                "data":None,
                "message":"Customer does not have capyMax account"
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST) 
        
class UpdateCustomerCapyBoostBalanceApiView(APIView):
    def get(self,request,id):
        try:
            if app_permissions.CAN_VIEW_CUSTOMER_ACCOUNT not in request.user.get_user_permissions():
                    res={
                        "status":"Failed",
                        "data":None,
                        "message":PERMISSION_MESSAGE
                    }
                    return Response(res,status=status.HTTP_403_FORBIDDEN)
            account=CapyBoostBalance.objects.get(id=id)
            res={
                "status":"success",
                "data":CapyBoostBalanceReadSerializer(account).data,
                "message":"CapyBoost Account fetch Successfully"
            }
            return Response(res,status=status.HTTP_200_OK)  
        except CapyBoostBalance.DoesNotExist as e:
            res={
                "status":"Failed",
                "data":None,
                "message":"Customer does not have capyBoost account"
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)   
        
    @swagger_auto_schema(
            request_body=UpdateCustomeCapyBoostBalanceSerializer
    )
    def put(self,request,id):
        try:
            if app_permissions.CAN_VIEW_CUSTOMER_ACCOUNT not in request.user.get_user_permissions():
                    res={
                        "status":"Failed",
                        "data":None,
                        "message":PERMISSION_MESSAGE
                    }
                    return Response(res,status=status.HTTP_403_FORBIDDEN)
            account=CapyBoostBalance.objects.get(id=id)
            serializer=UpdateCustomeCapyBoostBalanceSerializer(instance=account,data=request.data)
            serializer.is_valid(raise_exception=True)
            account.remaining_balance=serializer.validated_data["remaining_balance"]
            account.save()
            res={
                "status":"success",
                "data":None,
                "message":"CapyBoost Balance updated Successfully"
            }
            return Response(res,status=status.HTTP_200_OK)  
        except CapyBoostBalance.DoesNotExist as e:
            res={
                "status":"Failed",
                "data":None,
                "message":"Customer does not have capyBoost account"
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST) 
        
class CapyBoostCustomersBalanceApiview(APIView):
    @swagger_auto_schema(
            manual_parameters=[
                Parameter("search",IN_QUERY,type="str",required=False)
            ]
    )
    def get(self,request):
        try:
            if app_permissions.CAN_VIEW_CUSTOMER_ACCOUNT not in request.user.get_user_permissions():
                    res={
                        "status":"Failed",
                        "data":None,
                        "message":PERMISSION_MESSAGE
                    }
                    return Response(res,status=status.HTTP_403_FORBIDDEN)
            search=request.GET.get("search",None)
            account=CapyBoostBalance.objects.select_related("customer").order_by("-created_at").all()
            if search:
                account=account.filter(customer__email=search,customer_code=search)
            res={
                "status":"success",
                "data":CapyBoostBalanceReadSerializer(account,many=True).data,
                "message":"CapyBoost Account fetch Successfully"
            }
            return Response(res,status=status.HTTP_200_OK)  
        except CapyBoostBalance.DoesNotExist as e:
            res={
                "status":"Failed",
                "data":None,
                "message":"Customer does not have capyBoost account"
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)