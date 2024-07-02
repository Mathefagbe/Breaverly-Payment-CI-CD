from django.shortcuts import render
from pprint import pprint
from beaverly_api.serializer import (
    KycImageReadSerializer,
    KycDetailReadSerializer,
    KycDetailWriteSerializer,
    KycSelfieReadSerializer,
    KycUtilityBillsReadSerializer,
    LivePhotoKycReadSerializer,
    UploadKycFileSerializer,
    UpdateKycStatusSerializer,

)
from itertools import chain
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser,FormParser,MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
# Create your views here.
from beaverly_api.serializer import ImageUploadSerializer
from beaverly_api.models import KycDetails,KycDocumentImage,KycSelfie,KycUtilityBills,LivePhotoKyc
from beaverly_api import permissions as app_permissions
from drf_yasg.openapi import IN_QUERY, Parameter
import math
INSUFFICIENT_PERMISSION="INSUFFICIENT_PERMISSION"
PERMISSION_MESSAGE="PERMISSION DENIED"


class UploadedKycPhotoApiView(APIView):
    parser_classes=[JSONParser,FormParser,MultiPartParser]
    @swagger_auto_schema(
            request_body=ImageUploadSerializer
    )
    def post(self,request):
        try:
            serializer=ImageUploadSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            #check if he has uploaded before
            details,created=KycDocumentImage.objects.update_or_create(
                user=request.user,
                defaults=serializer.validated_data,
            )
            res={
                "status":"success",
                "data":None,
                "message":"Photo Uploaded Successfully"
            }
            return Response(res,status=status.HTTP_200_OK)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)

class AdminGetUploadedKycPhotoApiView(APIView):
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
            #check Permission
            if app_permissions.CAN_VERIFY_CUSTOMER_KYC not in request.user.get_user_permissions():
                    res={
                        "status":"Failed",
                        "data":None,
                        "message":PERMISSION_MESSAGE
                    }
                    return Response(res,status=status.HTTP_403_FORBIDDEN)
            kycphoto=KycDocumentImage.objects.select_related("user").all()
            paginated=kycphoto[((page-1) * limit):((page-1) *limit)+limit]
            total_items=len(kycphoto)
            res={
                "status":"success",
                "data":KycImageReadSerializer(paginated,many=True,context={'request':request}).data,
                "meta_data":{
                    "total_page":math.ceil(total_items / limit),
                    "current_page":page,
                    "per_page":limit,
                    "total":total_items
                },
                "message":"Photo Uploaded Successfully"
            }
            return Response(res,status=status.HTTP_200_OK)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)

class AdminUpdateUploadedKycPhotoApiView(APIView):
    @swagger_auto_schema(
              request_body=UpdateKycStatusSerializer
    )
    def put(self,request,id):
        try:
            #check Permission
            if app_permissions.CAN_VERIFY_CUSTOMER_KYC not in request.user.get_user_permissions():
                    res={
                        "status":"Failed",
                        "data":None,
                        "message":PERMISSION_MESSAGE
                    }
                    return Response(res,status=status.HTTP_403_FORBIDDEN)
            kycphoto=KycDocumentImage.objects.select_related("user").get(pk=id)
            serializer=UpdateKycStatusSerializer(instance=kycphoto,data=request)
            serializer.is_valid(raise_exception=True)
            kycphoto.status=serializer.validated_data["status"]
            kycphoto.save()
            res={
                "status":"success",
                "data":"Kyc Status Successfully",
                "message":"Kyc Status Successfully"
            }
            return Response(res,status=status.HTTP_200_OK)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)


class UploadedKycSelfieApiView(APIView):
    parser_classes=[JSONParser,FormParser,MultiPartParser]
    @swagger_auto_schema(
            request_body=ImageUploadSerializer
    )
    def post(self,request):
        try:
            serializer=ImageUploadSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            #check if he has uploaded before
            details,created=KycSelfie.objects.update_or_create(
                user=request.user,
                defaults=serializer.validated_data,
            )
            res={
                "status":"success",
                "data":None,
                "message":"Photo Uploaded Successfully"
            }
            return Response(res,status=status.HTTP_200_OK)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)

class AdminGetUploadedKycSelfieApiView(APIView):
    @swagger_auto_schema(
            manual_parameters=[
                Parameter("page",IN_QUERY,type="int",required=False),
                Parameter("limit",IN_QUERY,type="int",required=False),
            ]
    )
    def get(self,request):
        try:
            #check Permission
            page=int(request.GET.get("page",1))
            limit=int(request.GET.get("limit",10))
            if app_permissions.CAN_VERIFY_CUSTOMER_KYC not in request.user.get_user_permissions():
                    res={
                        "status":"Failed",
                        "data":None,
                        "message":PERMISSION_MESSAGE
                    }
                    return Response(res,status=status.HTTP_403_FORBIDDEN)
            kycphoto=KycSelfie.objects.select_related("user").all()
            paginated=kycphoto[((page-1) * limit):((page-1) *limit)+limit]
            total_items=len(kycphoto)
            res={
                "status":"success",
                "data":KycSelfieReadSerializer(paginated,many=True,context={'request':request}).data,
                "meta_data":{
                    "total_page":math.ceil(total_items / limit),
                    "current_page":page,
                    "per_page":limit,
                    "total":total_items
                },
                "message":"Photo Uploaded Successfully"
            }
            return Response(res,status=status.HTTP_200_OK)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)

class AdminUpdateUploadedKycSelfieApiView(APIView):
    @swagger_auto_schema(
              request_body=UpdateKycStatusSerializer
    )
    def put(self,request,id):
        try:
            #check Permission
            if app_permissions.CAN_VERIFY_CUSTOMER_KYC not in request.user.get_permission:
                    res={
                        "status":"Failed",
                        "data":None,
                        "message":PERMISSION_MESSAGE
                    }
                    return Response(res,status=status.HTTP_403_FORBIDDEN)
            kycselfie=KycSelfie.objects.select_related("user").get(pk=id)
            serializer=UpdateKycStatusSerializer(instance=kycselfie,data=request.data)
            serializer.is_valid(raise_exception=True)
            kycselfie.status=serializer.validated_data["status"]
            kycselfie.save()
            res={
                "status":"success",
                "data":"Kyc Status Successfully",
                "message":"Kyc Status Successfully"
            }
            return Response(res,status=status.HTTP_200_OK)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
        

class UploadedKycHoldingPhotoApiView(APIView):
    parser_classes=[JSONParser,FormParser,MultiPartParser]
    @swagger_auto_schema(
            request_body=ImageUploadSerializer
    )
    def post(self,request):
        try:
            serializer=ImageUploadSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            #check if he has uploaded before
            details,created=LivePhotoKyc.objects.update_or_create(
                user=request.user,
                defaults=serializer.validated_data,
            )
            res={
                "status":"success",
                "data":None,
                "message":"Photo Uploaded Successfully"
            }
            return Response(res,status=status.HTTP_200_OK)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)

class AdminGetUploadedLivePhotoKycApiView(APIView):
    @swagger_auto_schema(
            manual_parameters=[
                Parameter("page",IN_QUERY,type="int",required=False),
                Parameter("limit",IN_QUERY,type="int",required=False),
            ]
    )
    def get(self,request):
        try:
            #check Permission
            page=int(request.GET.get("page",1))
            limit=int(request.GET.get("limit",10))
            if app_permissions.CAN_VERIFY_CUSTOMER_KYC not in request.user.get_permission:
                    res={
                        "status":"Failed",
                        "data":None,
                        "message":PERMISSION_MESSAGE
                    }
                    return Response(res,status=status.HTTP_403_FORBIDDEN)
            kycphoto=LivePhotoKyc.objects.select_related("user").all()
            paginated=kycphoto[((page-1) * limit):((page-1) *limit)+limit]
            total_items=len(kycphoto)
            res={
                "status":"success",
                "data":LivePhotoKycReadSerializer(paginated,many=True,context={'request':request}).data,
                "meta_data":{
                    "total_page":math.ceil(total_items / limit),
                    "current_page":page,
                    "per_page":limit,
                    "total":total_items
                },
                "message":"Photo Uploaded Successfully"
            }
            return Response(res,status=status.HTTP_200_OK)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)

class AdminUpdateUploadedLivePhotoKycApiView(APIView):
    @swagger_auto_schema(
              request_body=UpdateKycStatusSerializer
    )
    def put(self,request,id):
        try:
            #check Permission
            if app_permissions.CAN_VERIFY_CUSTOMER_KYC not in request.user.get_permission:
                    res={
                        "status":"Failed",
                        "data":None,
                        "message":PERMISSION_MESSAGE
                    }
                    return Response(res,status=status.HTTP_403_FORBIDDEN)
            kyclive=LivePhotoKyc.objects.select_related("user").get(pk=id)
            serializer=UpdateKycStatusSerializer(instance=kyclive,data=request.data)
            kyclive.status=serializer.validated_data["status"]
            kyclive.save()
            res={
                "status":"success",
                "data":"Kyc Status Successfully",
                "message":"Kyc Status Successfully"
            }
            return Response(res,status=status.HTTP_200_OK)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
        

class UploadedKycUtilityBillApiView(APIView):
    parser_classes=[JSONParser,FormParser,MultiPartParser]
    @swagger_auto_schema(
            request_body=UploadKycFileSerializer
    )
    def post(self,request):
        try:
            serializer=UploadKycFileSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            #check if he has uploaded before
            details,created=KycUtilityBills.objects.update_or_create(
                user=request.user,
                defaults=serializer.validated_data,
            )
            res={
                "status":"success",
                "data":None,
                "message":"Photo Uploaded Successfully"
            }
            return Response(res,status=status.HTTP_200_OK)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)

class AdminGetUploadedKycUtilityBillApiView(APIView):
    @swagger_auto_schema(
            manual_parameters=[
                Parameter("page",IN_QUERY,type="int",required=False),
                Parameter("limit",IN_QUERY,type="int",required=False),
            ]
    )
    def get(self,request):
        try:
            #check Permission
            page=int(request.GET.get("page",1))
            limit=int(request.GET.get("limit",10))
            if app_permissions.CAN_VERIFY_CUSTOMER_KYC not in request.user.get_permission:
                    res={
                        "status":"Failed",
                        "data":None,
                        "message":PERMISSION_MESSAGE
                    }
                    return Response(res,status=status.HTTP_403_FORBIDDEN)
            kycphoto=KycUtilityBills.objects.select_related("user").all()
            paginated=kycphoto[((page-1) * limit):((page-1) *limit)+limit]
            total_items=len(kycphoto)
            res={
                "status":"success",
                "data":KycUtilityBillsReadSerializer(paginated,many=True,context={'request':request}).data,
                "meta_data":{
                    "total_page":math.ceil(total_items / limit),
                    "current_page":page,
                    "per_page":limit,
                    "total":total_items
                },
                "message":"Photo Uploaded Successfully"
            }
            return Response(res,status=status.HTTP_200_OK)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)

class AdminUpdateUploadedKycUtilityBillApiView(APIView):
    def put(self,request,id):
        try:
            #check Permission
            if app_permissions.CAN_VERIFY_CUSTOMER_KYC not in request.user.get_permission:
                    res={
                        "status":"Failed",
                        "data":None,
                        "message":PERMISSION_MESSAGE
                    }
                    return Response(res,status=status.HTTP_403_FORBIDDEN)
            kycutility=KycUtilityBills.objects.select_related("user").get(pk=id)
            serializer=UpdateKycStatusSerializer(instance=kycutility,data=request.data)
            kycutility.status=serializer.validated_data["status"]
            kycutility.save()
            res={
                "status":"success",
                "data":"Kyc Status Successfully",
                "message":"Kyc Status Successfully"
            }
            return Response(res,status=status.HTTP_200_OK)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
      

class KycFormDetalsApiView(APIView):
    '''
    Kyc Details can be created or edited with this endpoint
    '''
    @swagger_auto_schema(
           request_body=KycDetailWriteSerializer 
    )
    def post(self,request):
        try:
            serializer=KycDetailWriteSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            #In case of Update Check if he has before then delete and create again
            details,created=KycDetails.objects.update_or_create(
                user=request.user,
                defaults=serializer.validated_data,
            )
            res={
                "status":"success",
                "data":None,
                "message":"Kyc Details Uploaded Successfull"
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
            data=KycDetails.objects.filter(user=request.user).first()
            res={
                "status":"success",
                "data":KycDetailReadSerializer(data,context={'request':request}).data,
                "message":"Kyc Details fetched Successfull"
            }
            return Response(res,status=status.HTTP_200_OK)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
        
class KycVerificationUploadedStepApiView(APIView):
    def get(self,request):
        try:
            photo_verification=KycDocumentImage.objects\
                .select_related("user").filter(user=request.user).first()
            selfie_verification=KycSelfie.objects\
                .select_related("user").filter(user=request.user).first()
            holding_photo_verification=LivePhotoKyc.objects\
                .select_related("user").filter(user=request.user).first()
            utility_bill_verification=KycUtilityBills.objects\
            .select_related("user").filter(user=request.user).first()

            data=[]
            
            photo_data=KycImageReadSerializer(photo_verification,context={'request':request}).data
            photo_data["step"]="Photo"
            data.append(photo_data)

            selfie_data=KycSelfieReadSerializer(selfie_verification,context={'request':request}).data
            selfie_data["step"]="Selfie"
            data.append(selfie_data)

            holding_data=LivePhotoKycReadSerializer(holding_photo_verification,context={'request':request}).data
            holding_data["step"]="Holding_photo"
            data.append(holding_data)

            utility_data=KycUtilityBillsReadSerializer(utility_bill_verification,context={'request':request}).data
            utility_data["step"]="Utility Bill"
            data.append(utility_data)
           
            res={
                "status":"success",
                "data":data,
                "message":"User Kyc Upload Fetch Successfully"
            }
            return Response(res,status=status.HTTP_200_OK)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)