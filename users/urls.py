from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomPasswordResetForm

app_name = 'users'

urlpatterns = [
    path('', views.home, name='home'),
    # Authentication URLs
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('profile/', views.profile, name='profile'),
    
    # Password Reset URLs
    path('password-reset/', 
         views.CustomPasswordResetView.as_view(
             template_name='users/password_reset.html',
             email_template_name='users/password_reset_email.html',
             subject_template_name='users/password_reset_subject.txt',
             form_class=CustomPasswordResetForm
         ), 
         name='password_reset'),
    path('password-reset/done/', 
         views.CustomPasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), 
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         views.CustomPasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), 
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         views.CustomPasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), 
         name='password_reset_complete'),
    
    # Password Change URLs
    path('password-change/', 
         views.CustomPasswordChangeView.as_view(template_name='users/password_change.html'), 
         name='password_change'),
    path('password-change/done/', 
         views.CustomPasswordChangeDoneView.as_view(template_name='users/password_change_done.html'), 
         name='password_change_done'),
]
