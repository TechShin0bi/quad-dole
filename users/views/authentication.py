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
        # Get the 'next' parameter from the URL if it exists
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        # Default redirect for staff/superusers
        if self.request.user.is_staff or self.request.user.is_superuser:
            return reverse_lazy('admins:admin-dashboard')
        return reverse_lazy('app_urls:home')

    def form_valid(self, form):
        try:
            email = form.cleaned_data.get('username')
            user = form.get_user()
            
            if not user.is_active:
                messages.error(self.request, 'Your account is inactive. Please contact support.')
                return self.form_invalid(form)
                
            messages.success(self.request, f'Welcome back, {email}!')
            
            # Let the parent class handle the redirect
            return super().form_valid(form)
            
        except Exception as e:
            print(f"Login error: {str(e)}")
            messages.error(self.request, 'An error occurred during login. Please try again.')
            return self.form_invalid(form)

    def form_invalid(self, form):
        error_messages = []
        for field, errors in form.errors.items():
            for error in errors:
                error_messages.append(f"{form.fields[field].label if field in form.fields else field}: {error}")
        
        for msg in error_messages:
            messages.error(self.request, msg)
            
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