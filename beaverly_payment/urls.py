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
    SellCapySafePortFollioApiView,
    FetchRecipiantFullDetailsApiView,
    TransferToBeaverlyMemberApiView,
    WithdrawalAPiView,
    FetchMyBankDetailsAPiView,
    BalancesApiView
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
    url("sell_capyMax/portfolio/",SellCapyMAxPortFollioApiView.as_view()),

    url("fetch/recipient_email/<str:recipient_email>/",FetchRecipiantFullDetailsApiView.as_view()),
    url("transfer/",TransferToBeaverlyMemberApiView.as_view()),

    url("withdrawal/",WithdrawalAPiView.as_view()),
    url("fetch/my/bank_detail/",FetchMyBankDetailsAPiView.as_view()),

    url("balance/",BalancesApiView.as_view())

]

