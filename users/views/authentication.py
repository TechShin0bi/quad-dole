from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login
from django.contrib import messages
from django.shortcuts import redirect

from ..forms.authentication import UserLoginForm, UserRegisterForm
from ..models import User


class UserLoginView(LoginView):
    template_name = 'users/login.html'
    form_class = UserLoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('app_urls:home')

    def form_valid(self, form):
        email = form.cleaned_data.get('username')  # 'username' is actually email
        messages.success(self.request, f'Welcome back, {email}!')
        
        user = form.get_user()
        if user.is_staff or user.is_superuser:
            return redirect('admins:admin-dashboard')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid email or password.')
        return super().form_invalid(form)


class UserRegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        email = form.cleaned_data.get('email')
        messages.success(self.request, f'Account created for {email}. You can now log in.')
        return response
    
    
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('users:login')  # redirect after logout

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "Vous avez été déconnecté avec succès.")
        return super().dispatch(request, *args, **kwargs)