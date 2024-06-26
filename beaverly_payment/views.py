from django.shortcuts import render
from pprint import pprint
from .serializers import (
    TransactionWriteSerializer,
    TransactionReadSerializer,
    TopUpTransactionWriteSerializer,
    LeaverageTransactionWriteSerializer,
    AllDepositTransactionwriteSerializer,
    ChangeTransactionStatusSerializer,
    ContractDurationSerilaizer,
    RepaymentScheduleSerilaizer

)
from decimal import Decimal
from drf_yasg.openapi import IN_QUERY, Parameter
from itertools import chain
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser,FormParser,MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from .models import (
    TransactionHistory,ContractDuration,RepaymentSchedule
)
from django.db.models import Q
from beaverly_api import permissions as app_permissions
from .helper import generate_invoice_id,expire_date
from django.db import transaction
from dateutil.relativedelta import relativedelta
from beaverly_api.models import CapyBoostBalance,CapySafeAccount
from decimal import Decimal
INSUFFICIENT_PERMISSION="INSUFFICIENT_PERMISSION"
PERMISSION_MESSAGE="PERMISSION DENIED"

class DepositApiView(APIView):
    @swagger_auto_schema(
            request_body=TransactionWriteSerializer
    )
    def post(self,request):
        try:
            with transaction.atomic():
                serializer=TransactionWriteSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                contract_duration=serializer.validated_data["contract_duration"]

                #get the duration from the table
                durations=ContractDuration.objects.get(title__iexact=contract_duration)
                TransactionHistory.objects.create(
                    **serializer.validated_data,
                    initiated_by=request.user,
                    transaction_id=generate_invoice_id(),
                    expire_date=expire_date(durations.contract_duration),
                    credited_amount=serializer.validated_data["amount"]
                )
                res={
                    "status":"Success",
                    "data":None,
                    "message":"Desposit Successful"
                }
                return Response(res,status=status.HTTP_201_CREATED)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
        
class UserTransactionHistory(APIView):
    # @swagger_auto_schema(
    #         manual_parameters=[
    #             Parameter("search",IN_QUERY,type="str",required=False)
    #         ]
    # )
    def get(self,request):
        try:
            #todo paginations
            transaction_history=TransactionHistory.objects\
                .select_related("initiated_by").filter(initiated_by=request.user).order_by("-updated_at")
            res={
                "status":"Success",
                "data":TransactionReadSerializer(transaction_history,many=True,context={"request":request}).data,
                "message":"User Transaction History Fetch Successfully"
            }
            return Response(res,status=status.HTTP_201_CREATED)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
        
class AdminSingleTransactionApiView(APIView):
    def get(self,request,id):
        try:
            #Add permission
            if app_permissions.CAN_VIEW_TRANSACTION_HISTORY not in request.user.get_user_permissions():
                    res={
                        "status":"Failed",
                        "data":None,
                        "message":PERMISSION_MESSAGE
                    }
                    return Response(res,status=status.HTTP_403_FORBIDDEN)
            transaction_history=TransactionHistory.objects\
                .select_related("initiated_by").get(id=id)
            res={
                "status":"Success",
                "data":TransactionReadSerializer(transaction_history,context={"request":request}).data,
                "message":"User Transaction History Fetch Successfully"
            }
            return Response(res,status=status.HTTP_200_OK)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
            request_body=ChangeTransactionStatusSerializer
    )
    def put(self,request,id):
        try:
            #Add permission
            if app_permissions.CAN_VIEW_TRANSACTION_HISTORY not in request.user.get_user_permissions():
                    res={
                        "status":"Failed",
                        "data":None,
                        "message":PERMISSION_MESSAGE
                    }
                    return Response(res,status=status.HTTP_403_FORBIDDEN)
            transaction_history=TransactionHistory.objects.select_related("initiated_by").get(id=id)
            serializer=ChangeTransactionStatusSerializer(instance=transaction_history,data=request.data,partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            res={
                "status":"Success",
                "data":None,
                "message":"Transaction History updated Successfully"
            }
            return Response(res,status=status.HTTP_200_OK)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)

class AdminGetAllTransactionApiView(APIView):
    @swagger_auto_schema(
            manual_parameters=[
                Parameter("search",IN_QUERY,type="str",required=False,
                          description="admin can search with first_name,email and transaction_id")
            ]
    )
    def get(self,request):
        try:
            #Add permission
            if app_permissions.CAN_VIEW_TRANSACTION_HISTORY not in request.user.get_user_permissions():
                    res={
                        "status":"Failed",
                        "data":None,
                        "message":PERMISSION_MESSAGE
                    }
                    return Response(res,status=status.HTTP_403_FORBIDDEN)
            search=request.GET.get("search",None) #search by first_name,email or transaction_id
            transaction_history=TransactionHistory.objects\
                .select_related("initiated_by").order_by("-updated_at")
            if search:
                transaction_history=transaction_history\
                    .filter(Q(initiated_by__email=search)|Q(initiated_by__first_name=search)|Q(transaction_id=search))
            res={
                "status":"Success",
                "data":TransactionReadSerializer(transaction_history,many=True,context={"request":request}).data,
                "message":"User Transaction History Fetch Successfully"
            }
            return Response(res,status=status.HTTP_200_OK)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)

class TopUpDepositApiView(APIView):
    @swagger_auto_schema(
            request_body=TopUpTransactionWriteSerializer
    )

    def post(self,request):
        try:
            with transaction.atomic():
                serializer=TopUpTransactionWriteSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                account_type=serializer.validated_data["account_type"].lower()
                deposit_amount=serializer.validated_data["amount"]
                loan=CapyBoostBalance.objects.select_related("customer").filter(customer=request.user,expire_date__isnull=False)
                # # check if the top up amount is up to the payoff amount
                if loan and account_type == "capysafe":
                    # if loan[0].pay_off_amount:
                    if loan[0].remaining_balance == deposit_amount:
                        balance=loan[0].remaining_balance - deposit_amount
                        loan[0].remaining_balance=balance #if the money coming and the loan are the same
                        loan[0].expire_date=None
                        credited_amount=0.00
                        loan[0].save()
                    if  loan[0].remaining_balance > deposit_amount:
                        balance=loan[0].remaining_balance - deposit_amount #if the loan is more than the depost
                        loan[0].remaining_balance=balance
                        credited_amount=0.00
                        loan[0].save()
                    if loan[0].remaining_balance < deposit_amount:
                        balance=deposit_amount - loan[0].remaining_balance #if the loan is less than the depost
                        loan[0].remaining_balance=0.00
                        loan[0].expire_date=None
                        credited_amount=balance
                        loan[0].save()
                #todo check if user has leaverage before top
                TransactionHistory.objects.create(
                    **serializer.validated_data,
                    initiated_by=request.user,
                    transaction_id=generate_invoice_id(),
                    credited_amount= (credited_amount* Decimal(serializer.validated_data["transaction_fee"]))
                      if loan else (serializer.validated_data["amount"] * Decimal(serializer.validated_data["transaction_fee"]))

                )
                res={
                    "status":"Success",
                    "data":None,
                    "message":"TopUp Desposit Successful"
                }
                return Response(res,status=status.HTTP_201_CREATED)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
        
class LeaverageDepositApiView(APIView):
    @swagger_auto_schema(
            request_body=LeaverageTransactionWriteSerializer
    )
    def post(self,request):
        try:
            with transaction.atomic():
                serializer=LeaverageTransactionWriteSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                repayment_schedule=serializer.validated_data["repayment_schedule"]

                repayment=RepaymentSchedule.objects.get(title__iexact=repayment_schedule)
                #check if the user has any pending load
                capyboost=CapyBoostBalance.objects.select_related("customer").filter(customer=request.user)
                if capyboost.filter(expire_date__isnull=False).exists():
                    raise RuntimeError("You cant use CapyBoost Feature because you have unpaid loan")

                transaction_detail=TransactionHistory.objects.create(
                    **serializer.validated_data,
                    initiated_by=request.user,
                    transaction_id=generate_invoice_id(),
                    expire_date=expire_date(repayment.repayment_duration),
                    transaction_fee=repayment.transaction_fee,
                    credited_amount=serializer.validated_data["amount"] * Decimal(repayment.transaction_fee)
                )

                #update the expire date for the user contract
                CapySafeAccount.objects.select_related("customer").filter(customer=request.user).update(
                    expire_date=transaction_detail.expire_date,
                    account_status="ACTIVE",
                    # currency=transaction_detail.currency
                )
                loan,created=CapyBoostBalance.objects.update_or_create(
                    customer=request.user,
                    defaults={
                        "repayment_schedule":repayment_schedule,
                        "transaction_fee":transaction_detail.transaction_fee,
                        "deposit_percentage":transaction_detail.deposit_percentage,
                        "inital_deposit":transaction_detail.inital_deposit,
                        "loan_amount":transaction_detail.pay_off_amount, #payoffamount
                        "expire_date":transaction_detail.expire_date,
                        "remaining_balance":transaction_detail.pay_off_amount
                    }
                )
                #update that user capboost balance

                #Send Email Notification todo

                res={
                    "status":"Success",
                    "data":None,
                    "message":"Leaverage Desposit Successful"
                }
                return Response(res,status=status.HTTP_201_CREATED)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
        
class ContractDurationApiView(APIView):
    def get(self,request):
        try:
            queyset=ContractDuration.objects.all()
            data=ContractDurationSerilaizer(queyset,many=True).data
            res={
                "status":"Success",
                "data":data,
                "message":"contract Duration fetched Successfully"
            }
            return Response(res,status=status.HTTP_201_CREATED)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
        
class ReschedulePaymentApiView(APIView):
    def get(self,request):
        try:
            queyset=RepaymentSchedule.objects.all()
            data=RepaymentScheduleSerilaizer(queyset,many=True).data
            res={
                "status":"Success",
                "data":data,
                "message":"reschedule Payment fetched Successfully"
            }
            return Response(res,status=status.HTTP_201_CREATED)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)