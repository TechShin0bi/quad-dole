from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db import models
from django.utils.text import slugify
from django.urls import reverse, reverse_lazy
from django.db.models import Q, Count, Exists, OuterRef
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from products.models import Product, Category, Brand
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
        return Category.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_object()

        # --- Get all products in this category ---
        products_in_category = Product.objects.filter(category=category).select_related('model__brand')

        # --- Subcategories (for navigation or recommendations) ---
        subcategories = Category.objects.exclude(id=category.id)

        # --- Featured products ---
        featured_products = products_in_category[:4]

        # --- Paginate products ---
        paginator = Paginator(products_in_category.order_by('name'), self.paginate_by)
        page = self.request.GET.get('page', 1)
        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)

        # --- Related brands (brands that have products in this category) ---
        # brands = Brand.objects.filter(
        #     models__products__category=category
        # ).annotate(
        #     product_count=Count(
        #         'models__products',
        #         filter=Q(models__products__category=category),
        #         distinct=True
        #     )
        # ).order_by('name')

        # --- Update context ---
        context.update({
            'subcategories': subcategories,
            'featured_products': featured_products,
            'products': products,
            # 'brands': brands,
            'product_count': products_in_category.count(),
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
    template_name = 'products/update_category_form.html'
    
    def form_valid(self, form):
        messages.success(self.request, 'La catégorie a été mise à jour avec succès !')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('products:admin-category-detail', kwargs={'pk': self.object.pk})


class AdminCategoryDetailView(LoginRequiredMixin, StaffRequiredMixin, DetailView):
    """Admin-specific view for viewing detailed category information."""
    model = Category
    template_name = 'admin/category_detail.html'
    context_object_name = 'category'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_object()
        
        # Get all products in this category with additional details
        products = category.products.select_related('model__brand')
        
        # Get all categories except current one for reference
        other_categories = Category.objects.exclude(id=category.id)
        
        # Get related brands from products in this category through the model relationship
        related_brands = Brand.objects.filter(
            models.Exists(
                Product.objects.filter(
                    category=category,
                    model__brand=models.OuterRef('pk')
                )
            )
        ).distinct()
        
        # Add to context
        context.update({
            'products': products,
            'products_count': products.count(),
            'other_categories': other_categories,
            'related_brands': related_brands,
            'is_admin_view': True
        })
        
        return context


class CategoryDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Category
    template_name = 'products/category_confirm_delete.html'
    success_url = reverse_lazy('products:category-list')
    success_message = "La catégorie a été supprimée avec succès."

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)
