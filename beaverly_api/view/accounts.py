from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.template.loader import render_to_string
from beaverly_api.models import CapyMaxAccount,CapySafeAccount,CapyBoostBalance
from beaverly_payment.models import TransactionHistory
from django.db import transaction
from itertools import chain
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser,FormParser,MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from beaverly_api.helper import generate_low_risk_id, generate_smartpro_id,check_kyc_validations
from beaverly_api.serializer import (CapySafeAccountReadSerializer,CapyBoostBalanceReadSerializer,
    CapyMaxAccountReadSerializer,UpdateCustomeAccountBalanceSerializer,UpdateCustomeCapyBoostBalanceSerializer)
from drf_yasg.openapi import IN_QUERY, Parameter
from beaverly_api import permissions as app_permissions
from django.db.models import Q
from lock.thread import lock
import math
from notifications.emails import send_emails
INSUFFICIENT_PERMISSION="INSUFFICIENT_PERMISSION"
PERMISSION_MESSAGE="PERMISSION DENIED ONLY ADMIN CAN HAVE ACCESS"

class CreateCapyMaxAccountApiView(APIView):
    def post(self,request):
        try:
            #check if user has created before
            if CapyMaxAccount.objects.filter(customer=request.user).exists():
                raise RuntimeError("You have already created CapyMax Account")
            
            #check if he has completed his kyc
            check_kyc_validations(user=request.user)
            
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
        
class CreateCapySafeAccountApiView(APIView):
    def post(self,request):
        try:
            #check if user has created before
            if CapySafeAccount.objects.filter(customer=request.user).exists():
                raise RuntimeError("You have already created CapySafe Account")
            
            check_kyc_validations(request.user)

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
                Parameter("search",IN_QUERY,type="str",required=False,
                          description="admin can search with first_name,email and transaction_id"),
                Parameter("page",IN_QUERY,type="int",required=False),
                Parameter("limit",IN_QUERY,type="int",required=False),
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
            page=int(request.GET.get("page",1))
            limit=int(request.GET.get("limit",10))
            account=CapyMaxAccount.objects.select_related("customer").order_by("-created_at").all()
            if search:
                account=account.filter(Q(customer__email__icontains=search)|Q(customer_code=search)|Q(customer__first_name__icontains=search)|Q(customer__last_name__icontains=search))
            paginated=account[((page-1) * limit):((page-1) *limit)+limit]
            total_items=len(account)
            res={
                "status":"success",
                "data":CapyMaxAccountReadSerializer(paginated,many=True).data,
                "meta_data":{
                    "total_page":math.ceil(total_items / limit),
                    "current_page":page,
                    "per_page":limit,
                    "total":total_items
                },
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
                Parameter("search",IN_QUERY,type="str",required=False),
                Parameter("page",IN_QUERY,type="int",required=False),
                Parameter("limit",IN_QUERY,type="int",required=False),
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
            page=int(request.GET.get("page",1))
            limit=int(request.GET.get("limit",10))
            account=CapySafeAccount.objects.select_related("customer").order_by("-created_at")

            if search:
                account=account.filter(Q(customer__email__icontains=search)|Q(customer_code=search)|Q(customer__first_name__icontains=search)|Q(customer__last_name__icontains=search))
            paginated=account[((page-1) * limit):((page-1) *limit)+limit]
            total_items=len(account)
            res={
                "status":"success",
                "data":CapySafeAccountReadSerializer(paginated,many=True).data,
                "meta_data":{
                    "total_page":math.ceil(total_items / limit),
                    "current_page":page,
                    "per_page":limit,
                    "total":total_items
                },
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
        lock.acquire()
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
            account.balance +=serializer.validated_data["balance"]
            account.save()
            
            transactions=TransactionHistory.objects.filter(initiated_by=account.customer)\
                .only("status","transaction_id","transaction_type","created_at").latest()
            context={
                    "full_name":transactions.initiated_by.full_name,
                    "customer_name":transactions.initiated_by.full_name,
                    "customer_email":account.customer.email,
                    "amount":serializer.validated_data["balance"],
                    "date":account.updated_at.date(),
                    "transaction_id":transactions.transaction_id,
                    "transaction_type":transactions.transaction_type,
                    "status":transactions.status
            }
            #send email to user
            send_emails(
                 email=[account.customer.email],
                 subject="DEPOSIT SUCCESSFUL",
                 context=context,
                 template_name="success_transaction.html"
            )
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
        finally:
             lock.release()
           
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
        lock.acquire()
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
            account.balance +=serializer.validated_data["balance"]
            account.save()

            transactions=TransactionHistory.objects.filter(initiated_by=account.customer)\
                .only("status","transaction_id","transaction_type","created_at").latest()
            context={
                    "full_name":transactions.initiated_by.full_name,
                    "customer_name":transactions.initiated_by.full_name,
                    "customer_email":account.customer.email,
                    "amount":serializer.validated_data["balance"],
                    "date":account.updated_at.date(),
                    "transaction_id":transactions.transaction_id,
                    "transaction_type":transactions.transaction_type,
                    "status":transactions.status
            }
            #send email to user
            send_emails(
                 email=[account.customer.email],
                 subject="DEPOSIT SUCCESSFUL",
                 context=context,
                 template_name="success_transaction.html"
            )
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
        finally:
             lock.release()
        
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
        lock.acquire()
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
            account.payoff_amount +=serializer.validated_data["payoff_amount"]
            account.save()

            #update TransactionHistory
            transactions=TransactionHistory.objects.filter(initiated_by=account.customer)\
                .only("status","transaction_id","transaction_type","created_at").latest()
            context={
                    "full_name":transactions.initiated_by.full_name,
                    "customer_name":transactions.initiated_by.full_name,
                    "customer_email":account.customer.email,
                    "amount":serializer.validated_data["payoff_amount"],
                    "date":account.updated_at.date(),
                    "transaction_id":transactions.transaction_id,
                    "transaction_type":transactions.transaction_type,
                    "status":transactions.status
            }
            #send email to user
            send_emails(
                 email=[account.customer.email],
                 subject="LEVERAGE SUCCESSFUL",
                 context=context,
                 template_name="success_transaction.html"
            )
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
        finally:
             lock.release()
        
class CapyBoostCustomersBalanceApiview(APIView):
    @swagger_auto_schema(
            manual_parameters=[
                Parameter("search",IN_QUERY,type="str",required=False),
                Parameter("page",IN_QUERY,type="int",required=False),
                Parameter("limit",IN_QUERY,type="int",required=False),
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
            page=int(request.GET.get("page",1))
            limit=int(request.GET.get("limit",10))
            account=CapyBoostBalance.objects.select_related("customer").order_by("-created_at").all()
            if search:
                account=account\
                    .filter(Q(customer__email__icontains=search)|Q(customer_code=search)|Q(customer__first_name__icontains=search)|Q(customer__last_name__icontains=search))

            paginated=account[((page-1) * limit):((page-1) *limit)+limit]
            total_items=len(account)
            res={
                "status":"success",
                "data":CapyBoostBalanceReadSerializer(paginated,many=True).data,
                "meta_data":{
                    "total_page":math.ceil(total_items / limit),
                    "current_page":page,
                    "per_page":limit,
                    "total":total_items
                },
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


