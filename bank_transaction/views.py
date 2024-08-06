from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render, HttpResponse, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, View
from django.db import models
from .models import TransactionModel
from .forms import DepositForm, WithdrawForm, LoanRequestForm, TransferMoneyForm
from .constrant import DEPOSIT,LOAN,LOAN_PAID,WITHDRAWAL, TRANSFER_OUT, TRANSFER_IN
from django.contrib import messages
from datetime import datetime
from django.db.models import Sum
from django.urls import reverse_lazy
from bank_user.models import UserAccountModel
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
# Create your views here.
class TransactionCreateMixin(LoginRequiredMixin, CreateView):
    template_name = 'transaction_form.html'
    model = TransactionModel
    title = ''
    success_url = reverse_lazy('homePage')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account': self.request.user.account,
        })
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.title
        })
        return context
        
class DepositMoneyView(TransactionCreateMixin):
    form_class = DepositForm
    title = "Deposit"

    def get_initial(self):
        initial = {'transaction_type': DEPOSIT}
        return initial

    def form_valid(self, form):
        print("Form is valid")
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account
        print(f"Initial Balance: {account.balance}")
        print(f"Deposit Amount: {amount}")
        account.balance += amount
        print(f"Updated Balance: {account.balance}")
        account.save(update_fields=['balance'])
        messages.success(self.request, f"{amount}$ was deposited to your account successfully.")
        mail_subject = "Deposit Message"
        message = render_to_string('email_msg.html',{
            'user': self.request.user,
            'amount': amount,
        })
        to_email = self.request.user.email
        send_email = EmailMessage(mail_subject,message,to=[to_email])
        send_email.send()
        return super().form_valid(form)

    def form_invalid(self, form):
        print("Form is invalid")
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form))
class WithdrawMoneyView(TransactionCreateMixin):
    form_class = WithdrawForm
    title = "Withdraw"
    
    def get_initial(self):
        initial = {'transaction_type': WITHDRAWAL}
        return initial
    
    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account
        total_balance = UserAccountModel.objects.aggregate(total_balance=models.Sum('balance'))['total_balance']
        if total_balance is None or total_balance < amount:
            messages.error(self.request,f"The bank is bankrupt")
            return redirect('homePage')
        
        account.balance -= amount
        account.save(update_fields=['balance'])
        messages.success(self.request, f"{amount}$ was withdrawn from your account successfully.")
        return super().form_valid(form)

class LoanRequestView(TransactionCreateMixin):
    form_class = LoanRequestForm
    title = "Request For Loan"
    
    def get_initial(self):
        initial = {'transaction_type': LOAN}
        return initial
    
    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        current_loan_count = TransactionModel.objects.filter(account=self.request.user.account, transaction_type=LOAN, loan_approve=True).count()
        if current_loan_count > 3:
            return HttpResponse("You have crossed your loan limit.")
        messages.success(self.request, f"{amount}$ loan request for your account successfully.")
        return super().form_valid(form)
       
class TransactionReportView(LoginRequiredMixin, ListView):
    template_name = 'transaction_report.html'
    model = TransactionModel
    context_object_name = 'object_list'
    balance = 0

    def get_queryset(self):
        queryset = super().get_queryset().filter(account=self.request.user.account)
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            self.balance = TransactionModel.objects.filter(timestamp__date__gte=start_date, timestamp__date__lte=end_date).aggregate(Sum('amount'))['amount__sum']
        else:
            self.balance = self.request.user.account.balance
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'account': self.request.user.account,
        })
        return context
      
class PayLoanView(LoginRequiredMixin, View):
    def get(self, request, loan_id):
        loan = get_object_or_404(TransactionModel, id=loan_id)
        if loan.loan_approve:
            user_account = loan.account
            if loan.amount <= user_account.balance:
                user_account.balance -= loan.amount
                loan.balance_after = user_account.balance
                user_account.save()
                loan.transaction_type = LOAN_PAID
                loan.save()
                return redirect('loan_list')
            else:
                messages.error(self.request, f"Not enough balance to pay the loan!")
                return redirect('loan_list')
            
class LoanList(LoginRequiredMixin, ListView):
    model = TransactionModel
    template_name = 'loan_request.html'
    context_object_name = 'loans'
    
    def get_queryset(self):
        user_account = self.request.user.account
        queryset = TransactionModel.objects.filter(account=user_account, transaction_type=LOAN)
        return queryset
    
class TransferMoneyView(LoginRequiredMixin, View):
    form_class = TransferMoneyForm
    template_name = 'transfer_form.html'
    title = "Transfer Money With 1-Tap"
    
    def get(self, request, *args, **kwargs):
        form = self.form_class(user_account=request.user.account)
        context = {'form': form, 'title': self.title}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, user_account=request.user.account)
        if form.is_valid():
            from_account_no = request.user.account.account_no
            to_account_no = form.cleaned_data['to_account']
            amount = form.cleaned_data['amount']
            
            from_account = request.user.account
            to_account = get_object_or_404(UserAccountModel, account_no=to_account_no)
            
            from_account.balance -= amount
            to_account.balance += amount
            
            from_account.save()
            to_account.save()
            
            TransactionModel.objects.create(
                account=from_account,
                amount=-amount,
                balance_after_transaction=from_account.balance,
                transaction_type=TRANSFER_OUT,
            )
            TransactionModel.objects.create(
                account=to_account,
                amount=amount,
                balance_after_transaction=to_account.balance,
                transaction_type=TRANSFER_IN,
            )
            
            messages.success(request, f"Transferred {amount}$ to {to_account_no}.")
            return redirect('homePage')
        return render(request, self.template_name, {'form': form})