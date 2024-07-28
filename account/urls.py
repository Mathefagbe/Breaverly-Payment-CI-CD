from django.urls import path as url,re_path
from .views import (
                    EmailVerificationApiView,
                    VerifyOtpCodeAPiView,
                    UserRegistrationView,
                    LoginApiView,
                    PasswordResetApiView,
                    AdminUserRegistrationView,
                    InputPinSerializerApiView,
                    ChangePinSerializerApiView,
                    HideBalanceApiView,
                    TransactionOtpPinApiView,
                    VerifyTransactionPinApiView
                    )
urlpatterns = [
    url("auth/register/",UserRegistrationView.as_view()),
    url("auth/admin/register/",AdminUserRegistrationView.as_view()),
    url("auth/login/",LoginApiView.as_view()),
    url("auth/password/reset/",PasswordResetApiView.as_view()),
    url("auth/email/verification/",EmailVerificationApiView.as_view()),
    url("auth/otp/verification/",VerifyOtpCodeAPiView.as_view()),
    url("set/login/pin/",InputPinSerializerApiView.as_view()),
    url("update/login/pin/",ChangePinSerializerApiView.as_view()),
    url("hide-unhide/balance/",HideBalanceApiView.as_view()),
    url("send/pin/",TransactionOtpPinApiView.as_view()),
    url("verify/send/pin/<str:pin>/",VerifyTransactionPinApiView.as_view()),
]
