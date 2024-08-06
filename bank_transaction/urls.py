from django.urls import path
from .views import DepositMoneyView,WithdrawMoneyView,LoanRequestView,PayLoanView,TransactionReportView,LoanList,TransferMoneyView

urlpatterns = [
    path('deposit/',DepositMoneyView.as_view(),name='deposit_money'),
    path('withdraw/',WithdrawMoneyView.as_view(),name='withdraw_view'),
    path('loan-request/',LoanRequestView.as_view(),name='loan_request'),
    path('loan-paid/<int:loan_id>/',PayLoanView.as_view(),name='pay_loan'),
    path("loans/", LoanList.as_view(), name="loan_list"),
    path('report/',TransactionReportView.as_view(),name='trasaction_report'),
    path('transfer/', TransferMoneyView.as_view(), name='transfer'),
]
