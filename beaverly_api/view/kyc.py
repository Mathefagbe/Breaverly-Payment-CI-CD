from django.shortcuts import render
from pprint import pprint
from beaverly_api.serializer import (
    KycImageReadSerializer,
    KycDetailReadSerializer,
    KycDetailWriteSerializer,
    KycSelfieReadSerializer,
    KycUtilityBillsReadSerializer,
    LivePhotoKycReadSerializer,
    UploadKycFileSerializer

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
    def get(self,request):
        try:
            #check Permission
            if app_permissions.CAN_VERIFY_CUSTOMER_KYC not in request.user.get_user_permissions():
                    res={
                        "status":"Failed",
                        "data":None,
                        "message":PERMISSION_MESSAGE
                    }
                    return Response(res,status=status.HTTP_403_FORBIDDEN)
            kycphoto=KycDocumentImage.objects.select_related("user").all()
            res={
                "status":"success",
                "data":KycImageReadSerializer(kycphoto,many=True,context={'request':request}).data,
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
            kycphoto.has_verified=True
            kycphoto.save()
            res={
                "status":"success",
                "data":"Kyc Status verified Successfully",
                "message":"Kyc Status verified Successfully"
            }
            return Response(res,status=status.HTTP_200_OK)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)

class AdminUnVerifyUploadedKycPhotoApiView(APIView):
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
            kycphoto.has_verified=False
            kycphoto.save()
            res={
                "status":"success",
                "data":"Kyc Status Unverifed Successfully",
                "message":"Kyc Status Unverifed Successfully"
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
    parser_classes=[JSONParser,FormParser,MultiPartParser]
    def get(self,request):
        try:
            #check Permission
            if app_permissions.CAN_VERIFY_CUSTOMER_KYC not in request.user.get_user_permissions():
                    res={
                        "status":"Failed",
                        "data":None,
                        "message":PERMISSION_MESSAGE
                    }
                    return Response(res,status=status.HTTP_403_FORBIDDEN)
            kycphoto=KycSelfie.objects.select_related("user").all()
            res={
                "status":"success",
                "data":KycSelfieReadSerializer(kycphoto,many=True,context={'request':request}).data,
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
            kycphoto=KycSelfie.objects.select_related("user").get(pk=id)
            kycphoto.has_verified=True
            kycphoto.save()
            res={
                "status":"success",
                "data":"Kyc Status verified Successfully",
                "message":"Kyc Status verified Successfully"
            }
            return Response(res,status=status.HTTP_200_OK)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
        
class AdminUnverifyUploadedKycSelfieApiView(APIView):
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
            kycphoto=KycSelfie.objects.select_related("user").get(pk=id)
            kycphoto.has_verified=False
            kycphoto.save()
            res={
                "status":"success",
                "data":"Kyc Status Unverified Successfully",
                "message":"Kyc Status Unverified Successfully"
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
    def get(self,request):
        try:
            #check Permission
            if app_permissions.CAN_VERIFY_CUSTOMER_KYC not in request.user.get_permission:
                    res={
                        "status":"Failed",
                        "data":None,
                        "message":PERMISSION_MESSAGE
                    }
                    return Response(res,status=status.HTTP_403_FORBIDDEN)
            kycphoto=LivePhotoKyc.objects.select_related("user").all()
            res={
                "status":"success",
                "data":LivePhotoKycReadSerializer(kycphoto,many=True,context={'request':request}).data,
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
            kycphoto=LivePhotoKyc.objects.select_related("user").get(pk=id)
            kycphoto.has_verified=True
            kycphoto.save()
            res={
                "status":"success",
                "data":"Kyc Status Verified Successfully",
                "message":"Kyc Status Verified Successfully"
            }
            return Response(res,status=status.HTTP_200_OK)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)
        
class AdminUnVerifiedUploadedLivePhotoKycApiView(APIView):
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
            kycphoto=LivePhotoKyc.objects.select_related("user").get(pk=id)
            kycphoto.has_verified=False
            kycphoto.save()
            res={
                "status":"success",
                "data":"Kyc Status Unverified Successfully",
                "message":"Kyc Status Unverified Successfully"
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
    def get(self,request):
        try:
            #check Permission
            if app_permissions.CAN_VERIFY_CUSTOMER_KYC not in request.user.get_permission:
                    res={
                        "status":"Failed",
                        "data":None,
                        "message":PERMISSION_MESSAGE
                    }
                    return Response(res,status=status.HTTP_403_FORBIDDEN)
            kycphoto=KycUtilityBills.objects.select_related("user").all()
            res={
                "status":"success",
                "data":KycUtilityBillsReadSerializer(kycphoto,many=True,context={'request':request}).data,
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
            kycphoto=KycUtilityBills.objects.select_related("user").get(pk=id)
            kycphoto.has_verified=True
            kycphoto.save()
            res={
                "status":"success",
                "data":"Kyc Status verified Successfully",
                "message":"Kyc Status verifed Successfully"
            }
            return Response(res,status=status.HTTP_200_OK)
        except Exception as e:
            res={
                "status":"Failed",
                "data":None,
                "message":str(e)
            }
            return Response(res,status=status.HTTP_400_BAD_REQUEST)

class AdminUnverifiedUploadedKycUtilityBillApiView(APIView):
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
            kycphoto=KycUtilityBills.objects.select_related("user").get(pk=id)
            kycphoto.has_verified=False
            kycphoto.save()
            res={
                "status":"success",
                "data":"Kyc Status unverified Successfully",
                "message":"Kyc Status unverifed Successfully"
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