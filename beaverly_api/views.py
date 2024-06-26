from django.shortcuts import render
from .serializer import (
    EditProfileSerializer,
    PersonalDetailSerializer,
    WithdrawalDetailSerializer,
    BanksSerializers

)
from itertools import chain
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser,FormParser,MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from .models import Bank,CapyBoostBalance,CapyMaxAccount,CapySafeAccount


INSUFFICIENT_PERMISSION="INSUFFICIENT_PERMISSION"
PERMISSION_MESSAGE="PERMISSION DENIED"

class EditProfileApiView(APIView):
    parser_classes=[JSONParser,FormParser,MultiPartParser]

    def get(self,request):
        try:
            data=EditProfileSerializer(request.user).data
            res={
                "status":"success",
                "data":data,
                "message":"User profile fetch successfully"
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
        request_body=EditProfileSerializer
    )
    def put(self,request):
        try:
            serializer=EditProfileSerializer(instance=request.user,data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            res={
                "status":"success",
                "data":None,
                "message":"User Profile Updated Successfully"
            }
            return Response(res,status=status.HTTP_200_OK)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)

class PersonalDetailApiView(APIView):
    def get(self,request):
        try:
            data=PersonalDetailSerializer(request.user).data
            res={
                "status":"success",
                "data":data,
                "message":"Personal details fetch successfully"
            }
            return Response(res,status=status.HTTP_200_OK)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)

class WithdrawalDetailApiView(APIView):
    def get(self,request):
        try:
            data=WithdrawalDetailSerializer(request.user).data
            res={
                "status":"success",
                "data":data,
                "message":"withdrawal details fetch successfully"
            }
            return Response(res,status=status.HTTP_200_OK)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
        
class GetAllBanksApiView(APIView):
    def get(self,request):
        try:
            queryset=Bank.objects.all()
            data=BanksSerializers(queryset,many=True).data
            res={
                "status":"success",
                "data":data,
                "message":"List of banks fetched Successfully"
            }
            return Response(res,status=status.HTTP_200_OK)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST) 
        
class ProfileAccount(APIView):
    def get(self,request):
        try:
            capysafe=CapySafeAccount.objects.select_related("customer").filter(customer=request.user).first()
            capymax=CapyMaxAccount.objects.select_related("customer").filter(customer=request.user).first()
            capyboot=CapyBoostBalance.objects.select_related("customer").filter(customer=request.user).first()
            res={
                    "status":"success",
                    "data":[
                        {
                        "name":"CapySafe",
                        "amount":capysafe.balance,
                        "expire_date":capysafe.expire_date
                        },
                        {
                        "name":"CapyMax",
                        "amount":capymax.balance,
                        "expire_date":capymax.expire_date
                        },
                        {
                        "name":"CapyBoost",
                        "amount":capyboot.remaining_balance,
                        "expire_date":capyboot.expire_date
                        }
                ],
                "message":"customer account fetched successfull"
            }
            return Response(res,status=status.HTTP_200_OK)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST) 