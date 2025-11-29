from django.urls import path
from .views import (UserRegisterView, UserLoginView, CustomLogoutView, CustomPasswordResetView, CustomPasswordResetDoneView, CustomPasswordResetConfirmView, CustomPasswordResetCompleteView, CustomPasswordChangeView, CustomPasswordChangeDoneView)
from .forms import CustomPasswordResetForm
from .views import (
    UserListView, UserCreateView, 
    UserUpdateView, UserDeleteView
)
app_name = 'users'

urlpatterns = [
    
    # User Management URLs
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/add/', UserCreateView.as_view(), name='user-add'),
    path('users/<int:pk>/edit/', UserUpdateView.as_view(), name='user-edit'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user-delete'),
    
    # Authentication URLs
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('profile/', UserUpdateView.as_view(), name='profile'),
    
    # Password Reset URLs
    path('password-reset/', 
         CustomPasswordResetView.as_view(
             template_name='users/password_reset.html',
             email_template_name='users/password_reset_email.html',
             subject_template_name='users/password_reset_subject.txt',
             form_class=CustomPasswordResetForm
         ), 
         name='password_reset'),
    path('password-reset/done/', 
         CustomPasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), 
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         CustomPasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), 
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         CustomPasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), 
         name='password_reset_complete'),
    
    # Password Change URLs
    path('password-change/', 
         CustomPasswordChangeView.as_view(template_name='users/password_change.html'), 
         name='password_change'),
    path('password-change/done/', 
         CustomPasswordChangeDoneView.as_view(template_name='users/password_change_done.html'), 
         name='password_change_done'),
]
