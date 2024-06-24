from django.shortcuts import render
from pprint import pprint
from beaverly_api.serializer import (
    TransactionWriteSerializer,
    TransactionReadSerializer,
    TopUpTransactionWriteSerializer,
    LeaverageTransactionWriteSerializer

)
from itertools import chain
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser,FormParser,MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from beaverly_api.models import (
    TransactionHistory
)
from beaverly_api import permissions as app_permissions
from beaverly_api.helper import generate_invoice_id
from django.db import transaction

INSUFFICIENT_PERMISSION="INSUFFICIENT_PERMISSION"
PERMISSION_MESSAGE="PERMISSION DENIED"

class DepositApiView(APIView):
    @swagger_auto_schema(
            request_body=TransactionWriteSerializer
    )
    @transaction.atomic
    def post(self,request):
        try:
            serializer=TransactionWriteSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            TransactionHistory.objects.create(
                **serializer.validated_data,
                user=request.user,
                transaction_id=generate_invoice_id()
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
    @swagger_auto_schema(
            manual_parameters=[
                
            ]
    )
    def get(self,request):
        try:
            #todo paginations
            transaction_history=TransactionHistory.objects\
                .select_related("user").filter(user=request.user).order_by("-updated_at")
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
            pass
        except Exception as e:
            pass

    def put(self,request,id):
        try:
            pass
        except Exception as e:
            pass

class AdminGetAllTransactionApiView(APIView):
    def get(self,request):
        try:
            pass
        except Exception as e:
            pass

class TopUpDepositApiView(APIView):
    @swagger_auto_schema(
            request_body=TopUpTransactionWriteSerializer
    )
    @transaction.atomic
    def post(self,request):
        try:
            serializer=TopUpTransactionWriteSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            TransactionHistory.objects.create(
                **serializer.validated_data,
                user=request.user,
                transaction_id=generate_invoice_id()
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
    @transaction.atomic
    def post(self,request):
        try:
            serializer=LeaverageTransactionWriteSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            TransactionHistory.objects.create(
                **serializer.validated_data,
                user=request.user,
                transaction_id=generate_invoice_id()
            )
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