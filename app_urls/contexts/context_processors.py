from products.models import Brand
from orders.models import Order

def global_brands_data(request):
    brands_by_group = Brand.objects.all().order_by('name')
    order_count = 0
    if hasattr(request, 'user') and request.user.is_authenticated and request.user.is_staff:
        order_count = Order.objects.filter(status='pending').count()
    return {
        "all_brands": brands_by_group,
        "pending_orders_count": order_count
    }