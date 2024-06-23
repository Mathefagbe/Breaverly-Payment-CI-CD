from django.urls import path as url,re_path
from .views import (
    EditProfileApiView,
    PersonalDetailApiView,
    WithdrawalDetailApiView,
)
from beaverly_api.view.kyc import (
    AdminGetUploadedKycPhotoApiView,
    AdminGetUploadedKycSelfieApiView,
    AdminGetUploadedKycUtilityBillApiView,
    AdminGetUploadedLivePhotoKycApiView,
    AdminUpdateUploadedKycPhotoApiView,
    AdminUpdateUploadedKycSelfieApiView,
    AdminUpdateUploadedKycUtilityBillApiView,
    AdminUpdateUploadedLivePhotoKycApiView,
    UploadedKycHoldingPhotoApiView,
    UploadedKycPhotoApiView,
    UploadedKycSelfieApiView,
    UploadedKycUtilityBillApiView,
    KycVerificationUploadedStepApiView,
    KycFormDetalsApiView,
    AdminUnverifiedUploadedKycUtilityBillApiView,
    AdminUnVerifiedUploadedLivePhotoKycApiView,
    AdminUnVerifyUploadedKycPhotoApiView,
    AdminUnverifyUploadedKycSelfieApiView
)
from beaverly_api.view.deposit import (
    DepositApiView,
    UserTransactionHistory
)
urlpatterns = [
    url("user/profile/",EditProfileApiView.as_view()),
    url("user/personal/detail/",PersonalDetailApiView.as_view()),
    url("user/withdrawal/detail/",WithdrawalDetailApiView.as_view()),


    #--------------------KYC_ URLS-------------------------
    url("kyc/upload/photo/",UploadedKycPhotoApiView.as_view()),
    url("kyc/upload/selfie/",UploadedKycSelfieApiView.as_view()),
    url("kyc/upload/holding_ID/card/",UploadedKycHoldingPhotoApiView.as_view()),
    url("kyc/upload/utility/",UploadedKycUtilityBillApiView.as_view()),

    url("admin/get/kyc/photo/",AdminGetUploadedKycPhotoApiView.as_view()),
    url("admin/get/kyc/selfie/",AdminGetUploadedKycSelfieApiView.as_view()),
    url("admin/get/kyc/holding_id/cards/",AdminGetUploadedLivePhotoKycApiView.as_view()),
    url("admin/get/kyc/utility/",AdminGetUploadedKycUtilityBillApiView.as_view()),

    url("admin/verify/kyc/photo/<int:id>/",AdminUpdateUploadedKycPhotoApiView.as_view()),
    url("admin/verify/kyc/selfie/<int:id>/",AdminUpdateUploadedKycSelfieApiView.as_view()),
    url("admin/verify/kyc/holding_id/card/<int:id>/",AdminUpdateUploadedLivePhotoKycApiView.as_view()),
    url("admin/verify/kyc/utility/<int:id>/",AdminUpdateUploadedKycUtilityBillApiView.as_view()),

    url("admin/unverify/kyc/photo/<int:id>/",AdminUnVerifyUploadedKycPhotoApiView.as_view()),
    url("admin/unverify/kyc/selfie/<int:id>/",AdminUnverifyUploadedKycSelfieApiView.as_view()),
    url("admin/unverify/kyc/holding_id/card/<int:id>/",AdminUnVerifiedUploadedLivePhotoKycApiView.as_view()),
    url("admin/unverify/kyc/utility/<int:id>/",AdminUnverifiedUploadedKycUtilityBillApiView.as_view()),



    url("kyc/",KycVerificationUploadedStepApiView.as_view()),
    url("kyc/fill/form/",KycFormDetalsApiView.as_view()),

    #------------------KYC FINISHED-------------------------------

    #---------------TRANSACTION HISTORY AND DEPOSIT------------------

    url("deposit/",DepositApiView.as_view()),
    url("transaction/history/",UserTransactionHistory.as_view())
]