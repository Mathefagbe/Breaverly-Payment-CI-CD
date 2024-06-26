from django.urls import path as url,re_path
from .views import (
                    EmailVerificationApiView,
                    VerifyOtpCodeAPiView,
                    UserRegistrationView,
                    LoginApiView,
                    PasswordResetApiView,
                    AdminUserRegistrationView
                    )
urlpatterns = [
    url("auth/register/",UserRegistrationView.as_view()),
    url("auth/admin/register/",AdminUserRegistrationView.as_view()),
    url("auth/login/",LoginApiView.as_view()),
    url("auth/password/reset/",PasswordResetApiView.as_view()),
    url("auth/email/verification/",EmailVerificationApiView.as_view()),
    url("auth/otp/verification/",VerifyOtpCodeAPiView.as_view()),

]
