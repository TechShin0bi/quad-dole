from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, Count
from django.contrib.auth.mixins import LoginRequiredMixin

from ..models import ProductModel, Brand, Product
from products.forms.productmodel_forms import ProductModelForm
from .base import StaffRequiredMixin

class ProductModelListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = ProductModel
    template_name = 'products/productmodel_list.html'
    context_object_name = 'models'
    paginate_by = 20

    def get_queryset(self):
        # Annotate each product model with its product count
        queryset = ProductModel.objects.select_related('brand').annotate(
            product_count=Count('product_model', distinct=True)
        )
        
        # Search functionality
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(brand__name__icontains=search_query)
            )
        
        # Filter by brand
        brand_slug = self.request.GET.get('brand')
        if brand_slug:
            queryset = queryset.filter(brand__slug=brand_slug)
        
        # Filter by product count
        min_products = self.request.GET.get('min_products')
        if min_products and min_products.isdigit():
            queryset = queryset.filter(product_count__gte=int(min_products))
        
        # Ordering
        order_by = self.request.GET.get('order_by', 'brand__name')
        if order_by in ['name', '-name', 'created_at', '-created_at', 'product_count', '-product_count', 'brand__name', '-brand__name']:
            queryset = queryset.order_by(order_by)
        else:
            queryset = queryset.order_by('brand__name', 'name')
            
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all brands for filter dropdown
        brands = Brand.objects.all().order_by('name')
        
        # Get filter values from request
        search_query = self.request.GET.get('q', '')
        selected_brand = self.request.GET.get('brand', '')
        min_products = self.request.GET.get('min_products', '')
        order_by = self.request.GET.get('order_by', 'name')
        
        # Add filter values to context
        context.update({
            'brands': brands,
            'search_query': search_query,
            'selected_brand': selected_brand,
            'min_products': min_products,
            'order_by': order_by,
            'order_options': [
                ('name', 'Name (A-Z)'),
                ('-name', 'Name (Z-A)'),
                ('-created_at', 'Newest First'),
                ('created_at', 'Oldest First'),
                ('product_count', 'Product Count (Low to High)'),
                ('-product_count', 'Product Count (High to Low)')
            ]
        })
        
        # Add filter URL for pagination
        query_params = self.request.GET.copy()
        if 'page' in query_params:
            del query_params['page']
        context['query_params'] = query_params.urlencode()
        
        return context


class ProductModelDetailView(DetailView):
    model = ProductModel
    template_name = 'products/productmodel_detail.html'
    context_object_name = 'model'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_model = self.object
        
        # Get all categories that include this product model
        categories = product_model.product_model.all()  # Using the related_name from Category.models
        
        # Get products from these categories
        products = Product.objects.filter(
            category__in=categories
        ).select_related('category').distinct()
        
        context['products'] = products
        return context






class ProductModelCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = ProductModel
    form_class = ProductModelForm
    template_name = 'products/productmodel_form.html'
    success_message = "Le modèle a été créé avec succès."

    def get_success_url(self):
        return reverse_lazy('products:productmodel-detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response


class ProductModelUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = ProductModel
    form_class = ProductModelForm
    template_name = 'products/productmodel_form.html'
    slug_url_kwarg = 'pk'
    success_message = "Le modèle a été mis à jour avec succès."

    def get_success_url(self):
        return reverse_lazy('products:productmodel-detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response


class ProductModelDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = ProductModel
    template_name = 'products/productmodel_confirm_delete.html'
    slug_url_kwarg = 'pk'
    success_url = reverse_lazy('products:productmodel-list')
    success_message = "Le modèle a été supprimé avec succès."

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)
