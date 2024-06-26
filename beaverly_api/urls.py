from django.urls import path as url,re_path
from .views import (
    EditProfileApiView,
    PersonalDetailApiView,
    WithdrawalDetailApiView,
    GetAllBanksApiView,
    ProfileAccount
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
)
from beaverly_api.view.accounts import (
    CreateCapyMaxAccountApiView,
    CreateCapySafeAccountApiView,
    CapyMaxCustomersAccountsApiview,
    CapySafeCustomersAccountsApiview,
    UpdateCustomerCapyMaxBalanceApiView,
    UpdateCustomerCapysafeBalanceApiView,
    UpdateCustomerCapyBoostBalanceApiView,
    CapyBoostCustomersBalanceApiview
)
urlpatterns = [
    url("customer/profile/",EditProfileApiView.as_view()),
    url("customer/personal/detail/",PersonalDetailApiView.as_view()),
    url("customer/withdrawal/detail/",WithdrawalDetailApiView.as_view()),
    url("customer/account/detail/",ProfileAccount.as_view()),
    # url("customers/"),

    url("banks/",GetAllBanksApiView.as_view()),

    #--------------------KYC_ URLS-------------------------
    url("kyc/upload/photo/",UploadedKycPhotoApiView.as_view()),
    url("kyc/upload/selfie/",UploadedKycSelfieApiView.as_view()),
    url("kyc/upload/holding_ID/card/",UploadedKycHoldingPhotoApiView.as_view()),
    url("kyc/upload/utility/",UploadedKycUtilityBillApiView.as_view()),

    url("admin/get/kyc/photo/",AdminGetUploadedKycPhotoApiView.as_view()),
    url("admin/get/kyc/selfie/",AdminGetUploadedKycSelfieApiView.as_view()),
    url("admin/get/kyc/holding_id/cards/",AdminGetUploadedLivePhotoKycApiView.as_view()),
    url("admin/get/kyc/utility/",AdminGetUploadedKycUtilityBillApiView.as_view()),

    url("admin/kyc/photo/status/<uuid:id>/update/",AdminUpdateUploadedKycPhotoApiView.as_view()),
    url("admin/kyc/selfie/status/<uuid:id>/update/",AdminUpdateUploadedKycSelfieApiView.as_view()),
    url("admin/kyc/holding_id/card/status/<uuid:id>/update/",AdminUpdateUploadedLivePhotoKycApiView.as_view()),
    url("admin/kyc/utility/status/<uuid:id>/update/",AdminUpdateUploadedKycUtilityBillApiView.as_view()),


    url("kyc/",KycVerificationUploadedStepApiView.as_view()),
    url("kyc/fill/form/",KycFormDetalsApiView.as_view()),

    #------------------KYC FINISHED-------------------------------

    url("capysafe/customer/account/",CreateCapySafeAccountApiView.as_view()),
    url("capymax/customer/account/",CreateCapyMaxAccountApiView.as_view()),
    url("capysafe/customers/",CapySafeCustomersAccountsApiview.as_view()),
    url("capymax/customers/",CapyMaxCustomersAccountsApiview.as_view()),
    url("capyboost/customers/",CapyBoostCustomersBalanceApiview.as_view()),
    url("capysafe/balance/<uuid:id>/update/",UpdateCustomerCapysafeBalanceApiView.as_view()),
    url("capymax/balance/<uuid:id>/update/",UpdateCustomerCapyMaxBalanceApiView.as_view()),
    url("capyboost/balance/<uuid:id>/update/",UpdateCustomerCapyBoostBalanceApiView.as_view()),
]