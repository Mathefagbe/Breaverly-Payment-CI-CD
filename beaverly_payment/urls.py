from django.urls import path as url,re_path
from .views import (
    DepositApiView,
    UserTransactionHistory,
    TopUpDepositApiView,
    LeaverageDepositApiView,
    AdminGetAllTransactionApiView,
    AdminSingleTransactionApiView,
    ReschedulePaymentApiView,
    ContractDurationApiView,
    SellCapyMAxPortFollioApiView,
    SellCapySafePortFollioApiView
)

urlpatterns = [
    #---------------TRANSACTION HISTORY AND DEPOSIT------------------

    url("deposit/",DepositApiView.as_view()),
    url("deposit/top_up/",TopUpDepositApiView.as_view()),
    url("deposit/capyboost/",LeaverageDepositApiView.as_view()),

    url("transaction/history/",UserTransactionHistory.as_view()),
    url("admin/transaction/history/",AdminGetAllTransactionApiView.as_view()),
    url("admin/transaction/history/<uuid:id>/",AdminSingleTransactionApiView.as_view()),

    url("contract/durations/",ContractDurationApiView.as_view()),
    url("reschedule/payment/",ReschedulePaymentApiView.as_view()),

    url("sell_capySafe/portfolio/",SellCapySafePortFollioApiView.as_view()),
    url("sell_capyMax/portfolio/",SellCapyMAxPortFollioApiView.as_view())

]