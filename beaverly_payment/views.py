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
    WithdrawalSerializer,
    WithdrawalbalanceSerializer,
    PendingWithdrawalbalanceSerializer

)
from notifications.emails import send_emails
import math
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
from lock.thread import lock

INSUFFICIENT_PERMISSION="INSUFFICIENT_PERMISSION"
PERMISSION_MESSAGE="PERMISSION DENIED"


class DepositApiView(APIView):
    parser_classes=[JSONParser,FormParser,MultiPartParser]
    @swagger_auto_schema(
            request_body=TransactionWriteSerializer
    )
    def post(self,request):
        lock.acquire()
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
                
                transactions=TransactionHistory.objects.create(
                    **serializer.validated_data,
                    initiated_by=request.user,
                    transaction_type="deposit",
                    transaction_id=generate_invoice_id(),
                    expire_date=expire_date(durations.contract_duration),
                    amount_settled=serializer.validated_data["amount"]
                )
                email=transactions.initiated_by.email
                context={
                    "full_name":transactions.initiated_by.full_name,
                    "customer_name":transactions.initiated_by.full_name,
                    "customer_email":email,
                    "amount":transactions.amount,
                    "settle_amount":transactions.amount_settled,
                    "date":transactions.created_at.date(),
                    "transaction_id":transactions.transaction_id,
                    "transaction_type":transactions.transaction_type
                }
                send_emails(
                    email=request.user.get_admins(),
                    context=context,
                    subject="Deposit Transaction".upper(),
                    template_name="deposit.html",
                    pdf_file=transactions.receipt
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
        finally:
            lock.release()
        
class UserTransactionHistory(APIView):
    @swagger_auto_schema(
            manual_parameters=[
                Parameter("page",IN_QUERY,type="int",required=False),
                Parameter("limit",IN_QUERY,type="int",required=False),
            ]
    )
    def get(self,request):
        try:
            page=int(request.GET.get("page",1))
            limit=int(request.GET.get("limit",10))
            #todo paginations
            transaction_history=TransactionHistory.objects\
                .select_related("initiated_by","received_by").filter(initiated_by=request.user).order_by("-updated_at")
            paginated=transaction_history[((page-1) * limit):((page-1) *limit)+limit]
            total_items=len(transaction_history)
            res={
                "status":"Success",
                "data":TransactionReadSerializer(paginated,many=True,context={"request":request}).data,
                "meta_data":{
                    "total_page":math.ceil(total_items / limit),
                    "current_page":page,
                    "per_page":limit,
                    "total":total_items
                },
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
        lock.acquire()
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
        finally:
            lock.release()

class AdminGetAllTransactionApiView(APIView):
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
            page=int(request.GET.get("page",1))
            limit=int(request.GET.get("limit",10))
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
                    .filter(Q(initiated_by__email=search)|Q(initiated_by__first_name=search)|Q(transaction_id=search)|Q(initiated_by__last_name=search))
                
            paginated=transaction_history[((page-1) * limit):((page-1) *limit)+limit]
            total_items=len(transaction_history)
            res={
                "status":"Success",
                "data":TransactionReadSerializer(paginated,many=True,context={"request":request}).data,
                "meta_data":{
                    "total_page":math.ceil(total_items / limit),
                    "current_page":page,
                    "per_page":limit,
                    "total":total_items
                },
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
        lock.acquire()
        try:
            with transaction.atomic():
                serializer=TopUpTransactionWriteSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                account_type=serializer.validated_data["account_type"].lower()
                deposit_amount=serializer.validated_data["amount"]
                transaction_fee=serializer.validated_data["transaction_fee"]
                loan=CapyBoostBalance.objects.select_related("customer").filter(customer=request.user,expire_date__isnull=False)
                # # check if the top up amount is up to the payoff amount
                net_amount=deposit_amount - Decimal(transaction_fee)
                if loan and account_type == "capysafe":
                    loan_amount_repaid,credited_amount=capyBoostTransaction(loan,deposit_amount,transaction_fee)
                #todo check if user has leaverage before top
                transactions=TransactionHistory.objects.create(
                    **serializer.validated_data,
                    initiated_by=request.user,
                    transaction_type="top_up",
                    amount_repaid=loan_amount_repaid if loan else Decimal(0.00),
                    transaction_id=generate_invoice_id(),
                    amount_settled= (credited_amount)
                      if loan else (net_amount)
                )
                email=transactions.initiated_by.email
                context={
                    "full_name":transactions.initiated_by.full_name,
                    "customer_name":transactions.initiated_by.full_name,
                    "customer_email":email,
                    "amount":transactions.amount,
                    "settle_amount":transactions.amount_settled,
                    "date":transactions.created_at.date(),
                    "transaction_id":transactions.transaction_id,
                    "transaction_type":transactions.transaction_type
                }
                send_emails(
                    email=request.user.get_admins(),
                    context=context,
                    subject="TopUp Deposit Transaction".upper(),
                    template_name="deposit.html",
                    pdf_file=transactions.receipt
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
        finally:
            lock.release()
        
class LeaverageDepositApiView(APIView):
    parser_classes=[JSONParser,FormParser,MultiPartParser]
    @swagger_auto_schema(
            request_body=LeaverageTransactionWriteSerializer
    )
    def post(self,request):
        lock.acquire()
        try:
            with transaction.atomic():
                serializer=LeaverageTransactionWriteSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                repayment_schedule=serializer.validated_data["repayment_schedule"]
                payback_amount=serializer.validated_data.pop("pay_off_amount")

                CapySafeAccount.objects.select_related("customer").get(customer=request.user)

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
                    amount_settled=serializer.validated_data["amount"],
                    pay_off_amount=payback_amount #payback amount
                )

                #update the expire date for the user contract
                CapySafeAccount.objects.select_related("customer").filter(customer=request.user).update(
                    expire_date=transaction_detail.expire_date,
                    account_status="ACTIVE",
                    # currency=transaction_detail.currency
                )
                #admin will update the safe account balance
                loan,created=CapyBoostBalance.objects.update_or_create(
                    customer=request.user,
                    defaults={
                        "repayment_schedule":repayment_schedule,
                        "transaction_fee":transaction_detail.transaction_fee,
                        "deposit_percentage":transaction_detail.deposit_percentage,
                        "inital_deposit":transaction_detail.inital_deposit,
                        "expire_date":transaction_detail.expire_date,
                        # "payoff_amount":payback_amount it wil be edited by admin
                    }
                )
                #update that user capboost balance

                #Send Email Notification todo
                email=transaction_detail.initiated_by.email
                context={
                    "full_name":transaction_detail.initiated_by.full_name,
                    "customer_name":transaction_detail.initiated_by.full_name,
                    "customer_email":email,
                    "amount":transaction_detail.amount,
                    "settle_amount":transaction_detail.amount_settled,
                    "date":transaction_detail.created_at.date(),
                    "transaction_id":transaction_detail.transaction_id,
                    "transaction_type":transaction_detail.transaction_type
                }
                send_emails(
                    email=request.user.get_admins(),
                    context=context,
                    subject="Leaverage Deposit Transaction".upper(),
                    template_name="deposit.html",
                    pdf_file=transaction_detail.receipt
                )

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

        except CapySafeAccount.DoesNotExist as e:
            res={
                "status":"Failed",
                "data":None,
                "message":"THIS FEATURE IS MEANT FOR CAPYSAFE CUSTOMER"
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
        lock.acquire()
        try:
            with transaction.atomic():
            #check if the amount enter is upto the avaliable amount
                serializer=AmountSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                amount=serializer.validated_data["amount"]
                account=CapySafeAccount.objects.get(customer=request.user)
                if amount > account.balance:
                    raise RuntimeError("Insufficent Balance")
                account.balance = account.balance - (amount + Decimal(0.98))
                account.save()

                #check if he has a loan or not
                loan=CapyBoostBalance.objects.select_related("customer").filter(customer=request.user,expire_date__isnull=False)
                if loan:
                    loan_amount_repaid,credited_amount=capyBoostTransaction(loan,amount,0.00) 
                    #0.00 show that no transaction fee deducted from the loan
                    
                    
                obj,created=Withdrawals.objects.get_or_create(
                    customer=request.user,
                    defaults={
                        "customer":request.user,
                        "balance":credited_amount if loan else amount
                    }
                )
                if not created: #get the object
                    obj.balance +=credited_amount if loan else amount
                    obj.save()

                TransactionHistory.objects.create(
                    initiated_by=request.user,
                    transaction_id=generate_invoice_id(),
                    account_type="CapySafe",
                    transaction_type="sell_portfolio",
                    amount=amount,
                    transaction_fee=0.98,
                    amount_repaid=loan_amount_repaid if loan else Decimal(0.00),
                    amount_settled= credited_amount if loan else amount,
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
        finally:
            lock.release()

class SellCapyMAxPortFollioApiView(APIView):
    @swagger_auto_schema(
            request_body=AmountSerializer
    )
    def post(self,request):
        lock.acquire()
        try:
            with transaction.atomic():
            #check if the amount enter is upto the avaliable amount
                serializer=AmountSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                amount=serializer.validated_data["amount"]
                account=CapyMaxAccount.objects.get(customer=request.user)
                if amount > account.balance:
                    raise RuntimeError("Insufficient Balance")
                account.balance = account.balance - (amount+ Decimal(0.98))
                account.save()

                #check if he has a loan or not

                obj,created=Withdrawals.objects.get_or_create(
                    customer=request.user,
                    defaults={
                        # "customer_code":account.customer_code,
                        "customer":request.user,
                        "balance":amount
                    }
                )
                if not created: #get the object
                    obj.balance +=amount
                    obj.save()

                TransactionHistory.objects.create(
                    initiated_by=request.user,
                    transaction_id=generate_invoice_id(),
                    account_type="CapyMax",
                    transaction_fee=0.98,
                    transaction_type="sell_portfolio",
                    amount=amount,
                    amount_settled=amount,
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
        finally:
            lock.release()

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
        lock.acquire()
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
                    loan_amount_repaid,sent_amount=capyBoostTransaction(loan,amount,0.00)
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
                    amount_repaid=loan_amount_repaid if loan else Decimal(0.00),
                    amount_settled=sent_amount,
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
        finally:
            lock.release()
        
class WithdrawalAPiView(APIView):
    @swagger_auto_schema(
            request_body=WithdrawalSerializer
    )
    def post(self,request):
        lock.acquire()
        try:
            with transaction.atomic():
                serializer=WithdrawalSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                amount=serializer.validated_data.pop("amount")

                #transaction fee

                #withdrawal money from withdrawal balance
                sender_balance=Withdrawals.objects.get(customer=request.user)

                if amount > sender_balance.balance:
                    raise RuntimeError("Insufficient withdrawable balance")
                #remove the money from user withdrawal balance
                sender_balance.balance -= amount
                sender_balance.save()
                
                #check if he has any leaverage
                loan=CapyBoostBalance.objects.select_related("customer").filter(customer=request.user,expire_date__isnull=False)
                if loan:
                    loan_amount_repaid,sent_amount=capyBoostTransaction(loan,amount,0.00)


                #check if the user has a pending balance he can sent to pending withdrawal
                obj,created=PendingWithdrawals.objects.get_or_create(
                    customer=request.user,
                    defaults={
                        "balance":sent_amount if loan else (amount - Decimal(0.97))
                    }
                )
                if not created:
                    if obj.balance != Decimal(0.00):
                        raise RuntimeError("You have pending withdrawal that has not been settled yet")
                    obj.balance += sent_amount if loan else (amount - Decimal(0.97))
                    obj.status="pending"
                    obj.save()
                #if he has a leaverage the leaverage is remove first before it enters pending withdrawal

                #log transaction
                transactions=TransactionHistory.objects.create(
                    initiated_by=request.user,
                    transaction_id=generate_invoice_id(),
                    transaction_type="withdrawal",
                    amount=amount,
                    amount_repaid=loan_amount_repaid if loan else Decimal(0.00),
                    amount_settled=sent_amount if loan else (amount - Decimal(0.97)),
                    status="pending",
                    bank_details=serializer.validated_data,
                    transaction_fee=0.97 #transaction fee
                    
                )
                email=transactions.initiated_by.email
                context={
                    "full_name":transactions.initiated_by.full_name,
                    "customer_name":transactions.initiated_by.full_name,
                    "customer_email":email,
                    "amount":transactions.amount,
                    "settle_amount":transactions.amount_settled,
                    "date":transactions.created_at.date(),
                    "transaction_id":transactions.transaction_id,
                    "transaction_type":transactions.transaction_type
                }
                #after transaction log send emails
                send_emails(
                    email=[email],
                    subject="Transaction Processing Update".upper(),
                    context=context,
                    template_name="transaction_update.html",
                )
                #send to admins
                send_emails(
                    email=request.user.get_admins(),
                    subject="Request to Process withdrawal".upper(),
                    context=context,
                    template_name="process_transaction.html",
                )
                res={
                        "status":"Success",
                        "data":None,
                        "message":"Withdrawal Successful"
                    }
                return Response(res,status=status.HTTP_201_CREATED)
        except Withdrawals.DoesNotExist  as e:
            res={
                "status":"Failed",
                "data":None,
                "message":"You cant withdrawal,sell your portfolio to withdrawal balance"
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
        except Exception  as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
        finally:
            lock.release()
        
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

#withdrawal balance
class WithdrawalBalanceApiView(APIView):
    @swagger_auto_schema(
            manual_parameters=[
                Parameter("page",IN_QUERY,type="int",required=False),
                Parameter("limit",IN_QUERY,type="int",required=False),
                Parameter("search",IN_QUERY,type="str",required=False),
            ]
    )
    def get(self,request):
        try:
            page=int(request.GET.get("page",1))
            limit=int(request.GET.get("limit",10))
            if app_permissions.CAN_VIEW_CUSTOMER_BALANCE not in request.user.get_user_permissions():
                    res={
                        "status":"Failed",
                        "data":None,
                        "message":PERMISSION_MESSAGE
                    }
                    return Response(res,status=status.HTTP_403_FORBIDDEN)
            search=request.GET.get("search",None)
            withdrawal=Withdrawals.objects.select_related("customer").order_by("-updated_at")
            if search:
                withdrawal=withdrawal.filter(Q(customer__email=search)|Q(customer__first_name__icontains=search)|Q(customer__last_name__icontains=search))
            paginated=withdrawal[((page-1) * limit):((page-1) *limit)+limit]
            total_items=len(withdrawal)
            res={
                "status":"Success",
                "data":WithdrawalbalanceSerializer(paginated,many=True,context={"request":request}).data,
                "meta_data":{
                    "total_page":math.ceil(total_items / limit),
                    "current_page":page,
                    "per_page":limit,
                    "total":total_items
                },
                "message":"User Withdrawal balance Fetch Successfully"
            }
            return Response(res,status=status.HTTP_200_OK)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
        
class PendingWithdrawalBalanceApiView(APIView):
    @swagger_auto_schema(
            manual_parameters=[
                Parameter("page",IN_QUERY,type="int",required=False),
                Parameter("limit",IN_QUERY,type="int",required=False),
                Parameter("search",IN_QUERY,type="str",required=False),
            ]
    )
    def get(self,request):
        try:
            page=int(request.GET.get("page",1))
            limit=int(request.GET.get("limit",10))
            if app_permissions.CAN_VIEW_CUSTOMER_BALANCE not in request.user.get_user_permissions():
                    res={
                        "status":"Failed",
                        "data":None,
                        "message":PERMISSION_MESSAGE
                    }
                    return Response(res,status=status.HTTP_403_FORBIDDEN)
            search=request.GET.get("search",None)
            withdrawal=PendingWithdrawals.objects.select_related("customer").order_by("-updated_at")
            if search:
                withdrawal=withdrawal.filter(Q(customer__email=search)|Q(customer__first_name__icontains=search)|Q(customer__last_name__icontains=search))
            paginated=withdrawal[((page-1) * limit):((page-1) *limit)+limit]
            total_items=len(withdrawal)
            res={
                "status":"Success",
                "data":PendingWithdrawalbalanceSerializer(paginated,many=True,context={"request":request}).data,
                "meta_data":{
                    "total_page":math.ceil(total_items / limit),
                    "current_page":page,
                    "per_page":limit,
                    "total":total_items
                },
                "message":"User PendingWithdrawal balance Fetch Successfully"
            }
            return Response(res,status=status.HTTP_200_OK)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
        
class DeletePendingWithdrawalBalanceApiView(APIView):
    def delete(self,request,id):
        try:
            if app_permissions.CAN_VIEW_CUSTOMER_BALANCE not in request.user.get_user_permissions():
                    res={
                        "status":"Failed",
                        "data":None,
                        "message":PERMISSION_MESSAGE
                    }
                    return Response(res,status=status.HTTP_403_FORBIDDEN)
            pending_withdrawal=PendingWithdrawals.objects.get(id=id)
            pending_withdrawal.delete()
            res={
                "status":"Success",
                "data":None,
                "message":"Pending Withdrawal Remove Successfully"
            }
            return Response(res,status=status.HTTP_200_OK)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)



            