from django.shortcuts import render
from beaverly_api.serializer import (
    EditProfileSerializer,
    PersonalDetailSerializer,
    WithdrawalDetailSerializer,
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
    @swagger_auto_schema(
            request_body=ImageUploadSerializer
    )
    def post(self,request):
        try:
            serializer=ImageUploadSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            #check if he has uploaded before
            kycphoto=KycDocumentImage.objects.filter(user=request.user)
            if kycphoto:
                kycphoto.delete() #Delete the old one
            KycDocumentImage.objects.create(
                **serializer.validated_data,
                user=request.user
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
            if app_permissions.CAN_VERIFY_CUSTOMER_KYC not in request.user.get_permission:
                    res={
                        "status":"Failed",
                        "data":None,
                        "message":PERMISSION_MESSAGE
                    }
                    return Response(res,status=status.HTTP_403_FORBIDDEN)
            kycphoto=KycDocumentImage.objects.select_related("user").all()
            res={
                "status":"success",
                "data":KycImageReadSerializer(kycphoto,many=True).data,
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
            if app_permissions.CAN_VERIFY_CUSTOMER_KYC not in request.user.get_permission:
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
                "data":"Kyc Status Updated Successfully",
                "message":"Kyc Status Updated Successfully"
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
    @swagger_auto_schema(
            request_body=ImageUploadSerializer
    )
    def post(self,request):
        try:
            serializer=ImageUploadSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            #check if he has uploaded before
            kycphoto=KycSelfie.objects.filter(user=request.user)
            if kycphoto:
                kycphoto.delete() #Delete the old one
            KycSelfie.objects.create(
                **serializer.validated_data,
                user=request.user
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
            kycphoto=KycSelfie.objects.select_related("user").all()
            res={
                "status":"success",
                "data":KycSelfieReadSerializer(kycphoto,many=True).data,
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
                "data":"Kyc Status Updated Successfully",
                "message":"Kyc Status Updated Successfully"
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
    @swagger_auto_schema(
            request_body=ImageUploadSerializer
    )
    def post(self,request):
        try:
            serializer=ImageUploadSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            #check if he has uploaded before
            kycphoto=LivePhotoKyc.objects.filter(user=request.user)
            if kycphoto:
                kycphoto.delete() #Delete the old one
            LivePhotoKyc.objects.create(
                **serializer.validated_data,
                user=request.user
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
                "data":LivePhotoKycReadSerializer(kycphoto,many=True).data,
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
                "data":"Kyc Status Updated Successfully",
                "message":"Kyc Status Updated Successfully"
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
    @swagger_auto_schema(
            request_body=UploadKycFileSerializer
    )
    def post(self,request):
        try:
            serializer=UploadKycFileSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            #check if he has uploaded before
            kycphoto=KycUtilityBills.objects.filter(user=request.user)
            if kycphoto:
                kycphoto.delete() #Delete the old one
            KycUtilityBills.objects.create(
                **serializer.validated_data,
                user=request.user
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
                "data":KycUtilityBillsReadSerializer(kycphoto,many=True).data,
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
                "data":"Kyc Status Updated Successfully",
                "message":"Kyc Status Updated Successfully"
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
    @swagger_auto_schema(
           request_body=KycDetailWriteSerializer 
    )
    def post(self,request):
        try:
            serializer=KycDetailWriteSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data=serializer.save(user=request)
            res={
                "status":"success",
                "data":KycDetailReadSerializer(data).data,
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
            
            photo_data=ImageUploadSerializer(photo_verification).data
            photo_data["step"]="1"

            selfie_data=ImageUploadSerializer(selfie_verification).data
            selfie_data["step"]="2"

            holding_data=ImageUploadSerializer(holding_photo_verification).data
            holding_data["step"]="3"

            utility_data=UploadKycFileSerializer(utility_bill_verification).data
            utility_data["step"]="5"

            data=data.extend(list(chain(photo_data,selfie_data,holding_data,utility_data)))

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