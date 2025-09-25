from django.shortcuts import render
from django.views.generic import TemplateView

def custom_error_view(request, template_name, status_code, context=None):
    """Helper function to render error templates with the correct status code"""
    if context is None:
        context = {}
    
    # Add some default context
    context.setdefault('status_code', status_code)
    
    return render(request, template_name, context=context, status=status_code)

def bad_request(request, exception=None):
    """400 error handler"""
    return custom_error_view(
        request,
        '400.html',
        400,
        {'error': 'Requête incorrecte'}
    )

def permission_denied(request, exception=None):
    """403 error handler"""
    return custom_error_view(
        request,
        '403.html',
        403,
        {'error': 'Permission refusée'}
    )

def page_not_found(request, exception=None):
    """404 error handler"""
    return custom_error_view(
        request,
        '404.html',
        404,
        {'error': 'Page non trouvée'}
    )

def server_error(request):
    """500 error handler"""
    return custom_error_view(
        request,
        '500.html',
        500,
        {'error': 'Erreur du serveur'}
    )

# Home view
class HomeView(TemplateView):
    template_name = 'products/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get featured products
        context['featured_products'] = Product.objects.filter(
            featured=True
        )[:8]
        
        # Get featured categories (categories with most products)
        context['featured_categories'] = Category.objects.annotate(
            product_count=Count('products')
        ).filter(product_count__gt=0).order_by('-product_count')[:6]
        
        # Get featured brands (brands with most products)
        context['featured_brands'] = Brand.objects.annotate(
            product_count=Count('products')
        ).filter(product_count__gt=0).order_by('-product_count')[:8]
        
        # Get latest products
        context['latest_products'] = Product.objects.order_by('-created_at')[:8]
        
        return context
