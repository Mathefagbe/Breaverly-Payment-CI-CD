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
    RepaymentScheduleSerilaizer,
    AmountSerializer,
    TransferToBeaverlyMemberSerializer,
    UserReadTransactionSerializer,
    WithdrawalSerializer

)
from django.contrib.auth import get_user_model
from decimal import Decimal
from drf_yasg.openapi import IN_QUERY, Parameter
from itertools import chain
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser,FormParser,MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from .models import (
    TransactionHistory,ContractDuration,RepaymentSchedule,Withdrawals,PendingWithdrawals
)
from django.db.models import Q
from beaverly_api import permissions as app_permissions
from .helper import generate_invoice_id,expire_date,capyBoostTransaction
from django.db import transaction
from beaverly_api.models import CapyBoostBalance,CapySafeAccount,CapyMaxAccount
from decimal import Decimal

INSUFFICIENT_PERMISSION="INSUFFICIENT_PERMISSION"
PERMISSION_MESSAGE="PERMISSION DENIED"

class DepositApiView(APIView):
    parser_classes=[JSONParser,FormParser,MultiPartParser]
    @swagger_auto_schema(
            request_body=TransactionWriteSerializer
    )
    def post(self,request):
        try:
            with transaction.atomic():
                serializer=TransactionWriteSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                contract_duration=serializer.validated_data["contract_duration"]
                account_type=serializer.validated_data["account_type"]

                #get the duration from the table
                durations=ContractDuration.objects.get(title__iexact=contract_duration)
                if account_type == "CapySafe":
                    obj,created=CapySafeAccount.objects.get_or_create(
                        customer=request.user,
                        defaults={
                            "expire_date":expire_date(durations.contract_duration)
                        }
                    )
                    if not created:
                        obj.expire_date=expire_date(durations.contract_duration)
                        obj.save()

                if account_type == "CapyMax":
                    obj,created=CapyMaxAccount.objects.get_or_create(
                        customer=request.user,
                        defaults={
                            "expire_date":expire_date(durations.contract_duration)
                        }
                    )
                    if not created:
                        obj.expire_date=expire_date(durations.contract_duration)
                        obj.save()

                TransactionHistory.objects.create(
                    **serializer.validated_data,
                    initiated_by=request.user,
                    transaction_type="deposit",
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
        except ContractDuration.DoesNotExist as e:
            res={
                "status":"Failed",
                "data":None,
                "message":"Wrong Contract Duration"
            }
            return Response(res,status=status.HTTP_404_NOT_FOUND)
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
    parser_classes=[JSONParser,FormParser,MultiPartParser]
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
                net_amount=deposit_amount - Decimal(serializer.validated_data["transaction_fee"])
                if loan and account_type == "capysafe":
                    credited_amount=capyBoostTransaction(loan,net_amount)
                #todo check if user has leaverage before top
                TransactionHistory.objects.create(
                    **serializer.validated_data,
                    initiated_by=request.user,
                    transaction_type="top_up",
                    transaction_id=generate_invoice_id(),
                    credited_amount= (credited_amount)
                      if loan else (net_amount)
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
    parser_classes=[JSONParser,FormParser,MultiPartParser]
    @swagger_auto_schema(
            request_body=LeaverageTransactionWriteSerializer
    )
    def post(self,request):
        try:
            with transaction.atomic():
                serializer=LeaverageTransactionWriteSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                repayment_schedule=serializer.validated_data["repayment_schedule"]
                payback_amount=serializer.validated_data.pop("pay_off_amount")

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
                    credited_amount=serializer.validated_data["amount"],
                    pay_off_amount=payback_amount #payback amount
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
                        "expire_date":transaction_detail.expire_date,
                        "payoff_amount":payback_amount
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
        except RepaymentSchedule.DoesNotExist as e:
            res={
                "status":"Failed",
                "data":None,
                "message":"Invalid RepaymentSchedule"
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)

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
        
class SellCapySafePortFollioApiView(APIView):
    @swagger_auto_schema(
            request_body=AmountSerializer
    )
    def post(self,request):
        try:
            with transaction.atomic():
            #check if the amount enter is upto the avaliable amount
                serializer=AmountSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                amount=serializer.validated_data["amount"]
                account=CapySafeAccount.objects.get(customer=request.user)
                if amount > account.balance:
                    raise RuntimeError("The amount you enter is more than your balance on this account")
                account.balance = account.balance - amount
                account.save()

                obj,created=Withdrawals.objects.get_or_create(
                    customer=request.user,
                    defaults={
                        # "customer_code":account.customer_code,
                        "customer":request.user,
                        "balance":amount - Decimal(0.98) 
                    }
                )
                if not created: #get the object
                    obj.balance +=(amount - Decimal(0.98))
                    obj.save()

                TransactionHistory.objects.create(
                    initiated_by=request.user,
                    transaction_id=generate_invoice_id(),
                    account_type="CapySafe",
                    transaction_type="sell_portfolio",
                    amount=amount,
                    credited_amount= amount - Decimal(0.98),
                    status="successful"
                )
                res={
                    "status":"Success",
                    "data":None,
                    "message":"Withdrawal Successful"
                }
                return Response(res,status=status.HTTP_201_CREATED)
        except CapySafeAccount.DoesNotExist as e:
            res={
                "status":"Failed",
                "data":None,
                "message":"Account Not Found"
            }
            return Response(res,status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)

class SellCapyMAxPortFollioApiView(APIView):
    @swagger_auto_schema(
            request_body=AmountSerializer
    )
    def post(self,request):
        try:
            with transaction.atomic():
            #check if the amount enter is upto the avaliable amount
                serializer=AmountSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                amount=serializer.validated_data["amount"]
                account=CapyMaxAccount.objects.get(customer=request.user)
                if amount > account.balance:
                    raise RuntimeError("The amount you enter is more than your balance on this account")
                account.balance = account.balance - amount
                account.save()

                obj,created=Withdrawals.objects.get_or_create(
                    customer=request.user,
                    defaults={
                        # "customer_code":account.customer_code,
                        "customer":request.user,
                        "balance":amount - Decimal(0.98) 
                    }
                )
                if not created: #get the object
                    obj.balance +=(amount - Decimal(0.98))
                    obj.save()

                TransactionHistory.objects.create(
                    initiated_by=request.user,
                    transaction_id=generate_invoice_id(),
                    account_type="CapyMax",
                    transaction_type="sell_portfolio",
                    amount=amount,
                    credited_amount=amount - Decimal(0.98),
                    status="successful"
                )
                res={
                    "status":"Success",
                    "data":None,
                    "message":"Withdrawal Successful"
                }
                return Response(res,status=status.HTTP_201_CREATED)
        except CapyMaxAccount.DoesNotExist as e:
            res={
                "status":"Failed",
                "data":None,
                "message":"Account Not Found"
            }
            return Response(res,status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)

class FetchRecipiantFullDetailsApiView(APIView):
    def get(self,request,recipient_email):
        try:
            user=get_user_model().objects.get(email=recipient_email)
            res={
                    "status":"Success",
                    "data":user.full_name,
                    "message":"Customer details fetch"
                }
            return Response(res,status=status.HTTP_201_CREATED)
        except get_user_model().DoesNotExist:
            res={
                "status":"Failed",
                "data":None,
                "message":"Invalid Email Customer Doesn't Exist"
            }
            return Response(res,status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
            
class TransferToBeaverlyMemberApiView(APIView):

    @swagger_auto_schema(
            request_body=TransferToBeaverlyMemberSerializer
    )
    def post(self,request):
        try:
            with transaction.atomic():
                serializer=TransferToBeaverlyMemberSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                email=serializer.validated_data["recipient_email"]
                amount=serializer.validated_data["amount"]

                sender_balance=Withdrawals.objects.get(customer=request.user)

                if amount > sender_balance.balance:
                    raise RuntimeError("Insufficient withdrawable balance")
                #remove the money from user withdrawal balance
                sender_balance.balance -= amount
                sender_balance.save()
                sent_amount=amount

                loan=CapyBoostBalance.objects.filter(customer=request.user,expire_date__isnull=False)
                if loan:
                    sent_amount=capyBoostTransaction(loan,amount)
                #check if the user has loan

                recipient=get_user_model().objects.get(email=email)
                #add the money to other user withdrawal acount
                obj,created=Withdrawals.objects.get_or_create(
                    customer=recipient,
                    defaults={
                        "customer":recipient,
                        "balance":sent_amount
                    }
                )
                #if he has money in it before update is money
                if not created:
                    obj.balance +=sent_amount
                    obj.save()
                #log the transaction
                TransactionHistory.objects.create(
                    initiated_by=request.user,
                    transaction_id=generate_invoice_id(),
                    transaction_type="Transfer",
                    amount=amount,
                    credited_amount=sent_amount,
                    status="successful",
                    received_by=recipient
                )
                res={
                    "status":"Success",
                    "data":None,
                    "message":"Transfer Successful"
                }
                return Response(res,status=status.HTTP_201_CREATED)

        except Withdrawals.DoesNotExist as e:
            res={
                "status":"Failed",
                "data":None,
                "message":""
            }
            return Response(res,status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
        
class WithdrawalAPiView(APIView):
    @swagger_auto_schema(
            request_body=WithdrawalSerializer
    )
    def post(self,request):
        try:
            with transaction.atomic():
                serializer=WithdrawalSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                amount=serializer.validated_data.pop("amount")

                net_amount= amount- Decimal(0.97) #transaction fee

                #withdrawal money from withdrawal balance
                sender_balance=Withdrawals.objects.get(customer=request.user)

                if amount > sender_balance.balance:
                    raise RuntimeError("Insufficient withdrawable balance")
                #remove the money from user withdrawal balance
                sender_balance.balance -= amount
                sender_balance.save()
                
                #check if he has any leaverage
                loan=CapyBoostBalance.objects.filter(customer=request.user,expire_date__isnull=False)
                if loan:
                    sent_amount=capyBoostTransaction(loan,net_amount)


                #check if the user has a pending balance he can sent to pending withdrawal
                obj,created=PendingWithdrawals.objects.get_or_create(
                    customer=request.user,
                    defaults={
                        "balance":sent_amount if loan else net_amount
                    }
                )
                if not created:
                    if obj.balance != Decimal(0.00):
                        raise RuntimeError("You have pending withdrawal that has not been settled yet")
                    obj.balance += sent_amount if loan else net_amount
                    obj.status="pending"
                    obj.save()
                #if he has a leaverage the leaverage is remove first before it enters pending withdrawal

                #log transaction
                TransactionHistory.objects.create(
                    initiated_by=request.user,
                    transaction_id=generate_invoice_id(),
                    transaction_type="withdrawal",
                    amount=amount,
                    credited_amount=sent_amount if loan else net_amount,
                    status="pending",
                    bank_details=serializer.validated_data,
                    transaction_fee=0.97
                    
                )
                res={
                        "status":"Success",
                        "data":None,
                        "message":"Withdrawal Successful"
                    }
                return Response(res,status=status.HTTP_201_CREATED)
        except Exception  as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
        
class FetchMyBankDetailsAPiView(APIView):
    def get(self,request):
        try:
            data=request.user
            res={
                "status":"Success",
                "data":{
                    "account_name":data.account_name,
                    "account_number":data.account_number,
                    "bank_name":data.bank_name
                },
                "message":"Bank Details Fetched Successfully"
            }
            return Response(res,status=status.HTTP_201_CREATED)
        except Exception  as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
        

class BalancesApiView(APIView):
    def get(self,request):
        try:
            pending=PendingWithdrawals.objects.select_related("customer").filter(customer=request.user).first()
            loan=CapyBoostBalance.objects.select_related("customer").filter(customer=request.user).first()
            withdrawal=Withdrawals.objects.select_related("customer").filter(customer=request.user).first()
            res={
                    "status":"success",
                    "data":[
                        {
                        "name":"Pending",
                        "amount":pending.balance if pending else 0.0,
                  
                        },
                        {
                        "name":"Withdrawal",
                        "amount":withdrawal.balance if withdrawal else 0.0,
            
                        },
                        {
                        "name":"Capyboost",
                        "amount":loan.payoff_amount if loan else 0.0,
              
                        }
                ],
                "message":"customer balance fetched successfull"
            }
            return Response(res,status=status.HTTP_200_OK)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)