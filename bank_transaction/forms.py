from typing import Any
from django import forms
from .models import TransactionModel
from bank_user.models import UserAccountModel
class TransactionForm(forms.ModelForm):
    class Meta:
        model = TransactionModel
        fields = ['amount','transaction_type']
        
    def __init__(self,*args, **kwargs):
        self.account = kwargs.pop('account')
        super().__init__(*args, **kwargs)
        self.fields['transaction_type'].disabled = True
        self.fields['transaction_type'].widget = forms.HiddenInput()
        
    def save(self, commit=True):
        self.instance.account = self.account
        self.instance.balance_after_transaction = self.account.balance
        return super().save()
    
    
class DepositForm(TransactionForm):
    def clean_amount(self):
        min_deposit_amount = 100
        amount = self.cleaned_data["amount"]
        if amount < min_deposit_amount:
            raise forms.ValidationError(
                f'You need to deposit at least {min_deposit_amount}$'
            )
        
        return amount
    
class WithdrawForm(TransactionForm):
    def clean_amount(self):
        account = self.account
        min_withdraw_amount = 500
        max_withdraw_amount = 20000
        balance = account.balance
        amount = self.cleaned_data["amount"]
        if amount < min_withdraw_amount:
            raise forms.ValidationError(
                f"You have to withdraw at least {min_withdraw_amount}$"
            )
        if amount > max_withdraw_amount:
            raise forms.ValidationError(
                f"You can not withdraw more that {max_withdraw_amount}$ at a time."
            )
        if amount > balance:
            raise forms.ValidationError(
                f"You have {balance}$ in your account."
            )
        return amount

class LoanRequestForm(TransactionForm):
    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        
        return amount
   
class TransferMoneyForm(forms.Form):
    from_account = forms.CharField(max_length=12,disabled=True)
    to_account = forms.CharField(max_length=12)
    amount = forms.DecimalField(max_digits=12,decimal_places=2)
    
    def __init__(self,*args, **kwargs):
        self.user_account = kwargs.pop('user_account')
        super().__init__(*args, **kwargs)
        self.fields['from_account'].initial = self.user_account.account_no
    
    def clean(self):
        cleaned_data = super().clean()
        from_account = self.user_account.account_no
        to_account = cleaned_data.get('to_account')
        amount = cleaned_data.get('amount')
        
        if not UserAccountModel.objects.filter(account_no = to_account).exists():
            raise forms.ValidationError("Account Not Found.")
        
        form_account_balance = self.user_account.balance
        if form_account_balance < amount:
            raise forms.ValidationError("Insufficient funds in your account.")
        
        return cleaned_data