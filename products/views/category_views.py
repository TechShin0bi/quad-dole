from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Count, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.mixins import LoginRequiredMixin

from products.models import Category, Brand
from ..forms.category_forms import CategoryForm
from .base import StaffRequiredMixin

class CategoryListView(ListView):
    model = Category
    template_name = 'products/category_list.html'
    context_object_name = 'categories'
    paginate_by = 20
    
    def get_queryset(self):
        # Get all categories with product count
        queryset = Category.objects.annotate(
            product_count=Count('products', distinct=True)
        )
        
        # Search functionality
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # Filter by product count
        min_products = self.request.GET.get('min_products')
        if min_products and min_products.isdigit():
            queryset = queryset.filter(product_count__gte=int(min_products))
        
        # Ordering
        order_by = self.request.GET.get('order_by', 'name')
        if order_by in ['name', '-name', 'product_count', '-product_count']:
            queryset = queryset.order_by(order_by)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        
        # Get filter values from request
        search_query = self.request.GET.get('q', '')
        min_products = self.request.GET.get('min_products', '')
        order_by = self.request.GET.get('order_by', 'name')
        
        # Add filter values to context
        context.update({
            'total_categories': queryset.count(),
            'search_query': search_query,
            'min_products': min_products,
            'order_by': order_by,
            'order_options': [
                ('name', 'Name (A-Z)'),
                ('-name', 'Name (Z-A)'),
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


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'products/category_detail.html'
    context_object_name = 'category'
    paginate_by = 12
    
    def get_queryset(self):
        return Category.objects.annotate(product_count=Count('products'))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_object()
        
        # Get subcategories with product counts
        subcategories = Category.objects.all()
        
        # Get featured products (first 4 products in this category)
        featured_products = category.products.all()[:4]
        
        # Get all products in this category for pagination
        all_products = category.products.all().order_by('name')
        
        # Get brands that have products in this category
        brands = Brand.objects.filter(
            products__category=category
        ).annotate(
            product_count=Count('products', filter=Q(products__category=category), distinct=True)
        ).order_by('name')
        
        # Pagination
        page = self.request.GET.get('page', 1)
        paginator = Paginator(all_products, self.paginate_by)
        
        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)
        
        context.update({
            'subcategories': subcategories,
            'featured_products': featured_products,
            'products': products,
            'brands': brands,
            'product_count': all_products.count(),
        })
        
        return context


class CategoryCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'products/category_form.html'
    success_url = reverse_lazy('products:category-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'La catégorie a été créée avec succès !')
        return super().form_valid(form)


class CategoryUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'products/category_form.html'
    
    def form_valid(self, form):
        messages.success(self.request, 'La catégorie a été mise à jour avec succès !')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('products:category-detail', kwargs={'slug': self.object.slug})


class CategoryDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Category
    template_name = 'products/category_confirm_delete.html'
    success_url = reverse_lazy('products:category-list')
    success_message = "La catégorie a été supprimée avec succès."

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)
