from django.shortcuts import render,redirect
from django.urls import reverse_lazy
from django import forms
from .forms import UserRegistrationForm,UpdateUser
from django.views.generic import FormView
from django.contrib.auth import login,logout,update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView,LogoutView
from django.contrib.auth.forms import AuthenticationForm,PasswordChangeForm
from django.contrib import messages
# Create your views here.

class UserRegistration(FormView):
    template_name = 'user_form.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('register')
    
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)
    
    def form_invalid(self, form):
        print("Form is invalid")
        print(form.errors, flush=True)
        return super().form_invalid(form)
    
    
class UserLoginView(LoginView):
    template_name = 'user_login.html'
    form_class = AuthenticationForm
    def get_success_url(self):
        return reverse_lazy('homePage')

class UserLogoutView(LogoutView):
    def get_success_url(self):
        if self.request.user.is_authenticated:
            logout(self.request)
        return reverse_lazy('homePage')
    
    
@login_required
def user_update(request):
    if request.method == 'POST':
        update_form = UpdateUser(request.POST, instance=request.user)
        if update_form.is_valid():
            update_form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('homePage')
    else:
        update_form = UpdateUser(instance=request.user)
    return render(request, 'user_update.html', {'form': update_form, 'type': 'Update Your Profile', 'btn_type': 'Update'})


@login_required
def password_change(request):
    if request.method == 'POST':
        pass_change = PasswordChangeForm(data=request.POST, user=request.user)
        if pass_change.is_valid():
            pass_change.save()
            messages.success(request, "Password changed successfully.")
            update_session_auth_hash(request, pass_change.user)
            logout(request)
            return redirect('userLogin')
    else:
        pass_change = PasswordChangeForm(user=request.user)
    return render(request, 'password_change.html', {'form': pass_change, 'type': 'Update Password Here', 'btn_type': 'Change Password'})
