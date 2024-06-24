from account.serializer import BanksSerializers
from django.utils import timezone
from django.contrib.auth import get_user_model
import string
from django.utils.crypto import get_random_string
from rest_framework.parsers import JSONParser,FormParser,MultiPartParser
from beaverly_api.models import Roles
from django.db import transaction
from rest_framework.views import APIView
from account.models import Bank
from rest_framework.response import Response
from rest_framework import status


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