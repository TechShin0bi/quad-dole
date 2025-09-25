"""
URL configuration for Core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.conf.urls import handler400, handler403, handler404, handler500
from users.views import home

# Import error handlers
from products.views.error_views import bad_request, permission_denied, page_not_found, server_error

# Configure error handlers
handler400 = 'products.views.error_views.bad_request'
handler403 = 'products.views.error_views.permission_denied'
handler404 = 'products.views.error_views.page_not_found'
handler500 = 'products.views.error_views.server_error'

urlpatterns = [
    # Home
    path('', home, name='home'),
    
    # Apps
    path('', include('products.urls')),
    path('users/', include('users.urls')),
path("admins/", include("admins.urls", namespace="admins")),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    
    # Development
    path("__reload__/", include("django_browser_reload.urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
