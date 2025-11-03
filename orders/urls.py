from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Customer URLs
    path('', views.OrderListView.as_view(), name='order_list'),
    path('create/', views.OrderCreateView.as_view(), name='order_create'),
    path('create/product/<int:product_id>/', views.OrderSingleProductView.as_view(), name='order_create_single'),
    path('<int:order_number>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('<int:order_number>/cancel/', views.OrderCancelView.as_view(), name='order_cancel'),
    
    # Admin URLs
    path('admin/orders/', views.AdminOrderListView.as_view(), name='admin_order_list'),
    path('admin/orders/<int:pk>/', views.AdminOrderDetailView.as_view(), name='admin_order_detail'),
    path('admin/orders/<int:pk>/update-status/', views.AdminOrderStatusUpdateView.as_view(), name='admin_order_update_status'),
]
